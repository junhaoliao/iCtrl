#  Copyright (c) 2021-2023 iCtrl Developers
# 
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.

import base64
import json
import logging
import os
import re
import uuid
from enum import IntEnum
from io import StringIO

import bcrypt
import sqlalchemy
from cachetools import TTLCache
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import session as flask_session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates

from .Profile import Profile
from ..utils import send_email, validate_password

ACTIVATION_TTL_SECOND = 60 * 30
RESEND_COOLDOWN_TTL_SECOND = 30

SESSION_CRYPT_SALT = b'>@\x05[N%\xcf]+\x82\xc3\xcd\xde\xa6a\xeb'


# provide different services depending on the type:
# 0: not activated (first time email not verified)
# 1: normal user
# more to be added...
class ActivationType(IntEnum):
    NOT_ACTIVATED = 0
    NORMAL_USER = 1


logger = logging.getLogger(__name__)


class DBProfile(Profile):

    def __init__(self, app):
        db_passwd = os.environ['DBPASSWD']
        db_address = os.environ['DBADDR']
        app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{db_passwd}@{db_address}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.db = db = SQLAlchemy(app)
        self.salt = bcrypt.gensalt()

        # key: user_id, value: activation code
        size = 1024
        self.activation_cache = TTLCache(maxsize=size, ttl=ACTIVATION_TTL_SECOND)
        logger.debug(f"activation_cache set up with {size}, expiration time = {ACTIVATION_TTL_SECOND}")

        # key: user_id, value: True (to indicate the entry exists; can be any dummy value)
        self.resend_cooldown = TTLCache(maxsize=size, ttl=RESEND_COOLDOWN_TTL_SECOND)
        logger.debug(f"resend_cooldown cache set up with {size}, expiration time = {RESEND_COOLDOWN_TTL_SECOND}")

        activation_email_template = '/var/www/ictrl/application/resources/activation_email_template.html'
        logger.debug(f"Opening {activation_email_template} in read-only mode")
        try:
            with open(activation_email_template, 'r') as f:
                self.activation_email_body_template = f.read()
        except IOError as e:
            logger.error(f"Failed to open {activation_email_template}, does file exist? Error: {e}")

        class User(db.Model):
            __table_args__ = {"schema": "ictrl"}

            id = db.Column(db.Integer, primary_key=True)
            sessions = db.relationship('Session', backref='user', lazy=True)

            username = db.Column(db.String, unique=True, nullable=False)

            @validates('username')
            def validate_username(self, key, username):
                try:
                    assert re.match("^[A-Za-z0-9_-]+$", username)
                except AssertionError as ae:
                    logger.error("User name should contain only letters, numbers, underscores and dashes")
                    raise ae

                return username

            # this field is for the hashed passwords
            # for the password requirements verifications, please see "self.add_user"
            password = db.Column(db.String, nullable=False)

            email = db.Column(db.String, unique=True, nullable=False)

            @validates('email')
            def validate_email(self, key, email):
                try:
                    assert re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)
                except AssertionError as ae:
                    logger.error(f'Invalid email address: "{email}"')
                    raise ae

                # FIXME: remove this utoronto mail restriction in the future
                try:
                    assert email.endswith('utoronto.ca')
                except AssertionError as ae:
                    logger.error(f"Currently, only UofT emails are supported, emails must end with utoronto.ca")
                    raise ae

                return email

            activation_type = db.Column(db.Integer, nullable=False, default=ActivationType.NOT_ACTIVATED)

            logger.info("Defined a database table: User")

        class Session(db.Model):
            __table_args__ = {"schema": "ictrl"}

            id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            user_id = db.Column(db.Integer, db.ForeignKey('ictrl.user.id'), nullable=False)

            host = db.Column(db.String, nullable=False)
            nickname = db.Column(db.String, nullable=True)

            @validates('nickname')
            def validate_nickname(self, key, nickname):
                try:
                    assert len(nickname) <= 8
                except AssertionError as ae:
                    logger.error('Entered nickname is too long')
                    raise ae

                return nickname

            username = db.Column(db.String, nullable=False)
            private_key = db.Column(db.Text, nullable=True)

            logger.info("Defined a database table: Session")

        class VNCCredentials(db.Model):
            __table_args__ = {"schema": "ictrl"}

            session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('ictrl.session.id'), primary_key=True,
                                   nullable=False)
            credentials = db.Column(db.Text, nullable=False)

            logger.info("Defined a database table: VNCCredentials")

        self.User = User
        self.Session = Session
        self.VNCCredentials = VNCCredentials

        # db.drop_all()
        db.engine.execute("CREATE SCHEMA IF NOT EXISTS ictrl;")
        db.create_all()
        logger.info("Created database SCHEMA ictrl and created all databases defined")

    def login(self, username, password):
        username = username.lower()
        password_bytes = password.encode('ascii')

        user = self.User.query.filter_by(username=username).first()
        hashed_password_bytes = user.password.encode('ascii')
        if (user is None) or (not bcrypt.checkpw(password_bytes, hashed_password_bytes)):
            #Reason being is for security concern, we want to be as ambiguous as possible
            #In a scenario a hacker wants to hack into an account
            #You wouldn't want him to know whether your username or your password is correct
            #If he guesses the username then he can guess the password next, given by the original error messages
            error_msg = 'ACCOUNT_WRONG_USERNAME or ACCOUNT_WRONG_PASSWORD'
            logger.error(error_msg)
            abort(403, error_msg)

        if user.activation_type == ActivationType.NOT_ACTIVATED:
            error_msg = 'ACCOUNT_NOT_ACTIVATED'
            logger.error(error_msg)
            abort(401, error_msg)

        flask_session.clear()
        flask_session['userid'] = user.id

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=32,
                         salt=SESSION_CRYPT_SALT,
                         iterations=1000000)
        flask_session['session_crypt_key'] = base64.urlsafe_b64encode(kdf.derive(password_bytes))

        return True

    @staticmethod
    def logout():
        # remove the username from the session if it's there
        userid = flask_session.pop('userid', None)
        logger.info(f'Removed session user: {userid}')

        return True

    def query(self):
        user = self.get_user()

        _profile = {
            "sessions": {}
        }

        for session in user.sessions:
            session_id = session.id.hex
            _profile["sessions"][session_id] = {
                "host": session.host,
                "nickname": session.nickname,
                "username": session.username
            }

        logger.info("Query user sessions successful")

        return _profile

    def add_user(self, username, password, email):
        # force lower case
        username = username.lower()
        email = email.lower()

        password_ok, password_reason = validate_password(password)
        if not password_ok:
            logger.warning(f'Password is not allowed, reason: {password_reason}')
            abort(422, password_reason)

        # hash the password before storing
        password = password.encode('ascii')
        hashed_password = bcrypt.hashpw(password, self.salt).decode('ascii')

        try:
            user = self.User(username=username, password=hashed_password, email=email)
            self.db.session.add(user)
            self.save_profile()

            self.send_activation_email(username)
        except AssertionError as e:
            # fails the validations as imposed by "@validates" above
            abort(422, e)
        except sqlalchemy.exc.IntegrityError as e:
            error_info = e.orig.args[0]
            if 'user_username_key' in error_info:
                error = 'Failed to add user: ACCOUNT_DUPLICATE_USERNAME'
                logger.error(error)
                abort(422, error)
            elif 'user_email_key' in error_info:
                error = 'Failed to add user: ACCOUNT_DUPLICATE_EMAIL'
                logger .error(error)
                abort(422, error)

            logger.error('Failed to add user: other reasons')
            abort(403, e)

        return True, ''

    def activate_user(self, userid, code):
        cached_code = self.activation_cache.get(userid, None)

        if not cached_code:
            return False
        elif cached_code == code:
            user = self.User.query.filter_by(id=userid).first()
            if user is None:
                error = f'Cannot find any matching user with userid={userid}'
                logger.error(error)
                abort(403, error)

            user.activation_type = ActivationType.NORMAL_USER
            self.save_profile()

            logger.info(f"Successfully activated user with userid={userid}")

            return True

        return False

    def get_user(self):
        if 'userid' not in flask_session:
            error = 'You are not logged in'
            logger.error(error)
            abort(403, error)
        userid = flask_session['userid']

        user = self.User.query.filter_by(id=userid).first()
        if user is None:
            error = f'Cannot find any matching record: userid = {userid}'
            logger.error(error)
            abort(403, error)

        logger.info(f'Successfully retrieved user with userid={userid}')
        return user

    def add_session(self, host, username, conn=None):
        user = self.get_user()
        try:
            session = self.Session(id=uuid.uuid4(), user=user, host=host, username=username)

            # commit to db first so that session.id can be read
            self.db.session.add(session)
            self.save_profile()

            if conn is not None:
                key_file_obj = StringIO()
                status, reason = conn.save_keys(key_file_obj=key_file_obj,
                                                public_key_comment=f'{session.id.hex}')
                if not status:
                    self.db.session.delete(session)
                    return status, reason

                clear_private_key = key_file_obj.getvalue().encode('ascii')
                f = Fernet(flask_session['session_crypt_key'])
                session.private_key = f.encrypt(clear_private_key).decode('ascii')

            self.save_profile()

            logger.info(f'Successfully added a new session: session_id = {session.id}')
        except AssertionError as e:
            logger.error(f'Error: {e}')
            abort(403, e)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(f'Error: {e}')
            abort(403, e)

        return True, ''

    def _get_session(self, session_id):
        if 'userid' not in flask_session:
            error = 'You are not logged in'
            logger.error(error)
            abort(403, error)
        userid = flask_session['userid']

        logger.info(f'Returning session, session_id = {session_id}')
        return self.Session.query.filter_by(id=session_id, user_id=userid).first()

    def delete_session(self, session_id):
        session = self._get_session(session_id)
        if session is None:
            return False, f'failed: session {session_id} does not exist'

        self.db.session.delete(session)
        self.save_profile()

        logger.info(f'Successfully deleted session, session_id = {session_id}')

        return True, ''

    def change_host(self, session_id, new_host):
        session = self._get_session(session_id)
        if session is None:
            return False, f'failed: session {session_id} does not exist'

        session.host = new_host
        self.save_profile()

        logger.info(f'Successfully changed host for session, session_id = {session_id}')

        return True, ''

    def save_profile(self):
        self.db.session.commit()
        logger.info("Profile saved")

    def get_session_info(self, session_id):
        session = self._get_session(session_id)
        if session is None:
            logger.debug(f"Session {session_id} does not exist, cannot retrieve session info")
            return None, None, None, None, None

        f = Fernet(flask_session['session_crypt_key'])
        crypt_key_bytes = session.private_key.encode('ascii')
        clear_private_key = f.decrypt(crypt_key_bytes).decode('ascii')

        return session.host, session.username, None, clear_private_key, session.nickname

    def set_session_nickname(self, session_id, nickname):
        session = self._get_session(session_id)
        if session is None:
            return False, f'failed: session {session_id} does not exist'

        session.nickname = nickname
        self.save_profile()

        logger.info(f'Successfully set session nickname={nickname} for session {session_id}')

        return True, ''

    def set_session_vnc_credentials(self, session_id, credentials):
        session = self._get_session(session_id)
        if session is None:
            return False, f'failed: session {session_id} does not exist'

        if credentials is None:
            # it is a delete request
            vnc_credential = self.VNCCredentials.query.filter_by(session_id=session_id).first()
            self.db.session.delete(vnc_credential)
            logger.info(f'Successfully deleted vnc credentials for session {session_id}')
        else:
            # it is an add / update request
            json_str = json.dumps(credentials)
            base64_str = base64.b64encode(json_str.encode('ascii')).decode('ascii')
            vnc_credential = self.VNCCredentials.query.filter_by(session_id=session_id).first()
            if vnc_credential is not None:
                # update
                vnc_credential.credentials = base64_str
            else:
                # add
                vnc_credential = self.VNCCredentials(session_id=session_id, credentials=base64_str)
                self.db.session.add(vnc_credential)
            logger.info(f'Successfully added/updated vnc credentials for session {session_id}')

        self.save_profile()

        return True, ''

    def get_session_vnc_credentials(self, session_id):
        logger.debug(f'Getting vnc credentials for session: {session_id}')
        session = self._get_session(session_id)
        if session is None:
            return False, f'failed: session {session_id} does not exist'

        vnc_credential = self.VNCCredentials.query.filter_by(session_id=session_id).first()
        if vnc_credential is None:
            return True, ''
        else:
            json_str = base64.b64decode(vnc_credential.credentials)
            return True, json.loads(json_str.decode('ascii'))

    def send_activation_email(self, username):
        user = self.User.query.filter_by(username=username).first()
        if user is None:
            error = f'Cannot find any matching user with username={username}'
            logger.error(error)
            abort(403, error)
        elif self.resend_cooldown.get(str(user.id), None):
            error = f'Too soon to resend. Please check your email junk box or try again in {RESEND_COOLDOWN_TTL_SECOND} seconds.'
            logger.error(error)
            abort(429, error)

        user_id = str(user.id)
        code = str(uuid.uuid4())
        self.activation_cache[user_id] = code
        self.resend_cooldown[user_id] = True

        body = self.activation_email_body_template.format(
            username=username,
            userid=user_id,
            code=code,
            expire_min=int(ACTIVATION_TTL_SECOND / 60))
        send_email(user.email, 'Activate Your iCtrl Account', body)

        logger.info(f'Successfully sent out activation email to email={user.email}')

        return True
