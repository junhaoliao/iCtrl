import base64
import os
import re
import uuid
from enum import IntEnum
from io import StringIO

import bcrypt
import sqlalchemy
from cachetools import TTLCache
from flask import session as flask_session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
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


class DBProfile:
    def __init__(self, app):
        db_passwd = os.environ['DBPASSWD']
        db_address = os.environ['DBADDR']
        app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{db_passwd}@{db_address}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.db = db = SQLAlchemy(app)
        self.salt = bcrypt.gensalt()

        # key: user_id, value: activation code
        self.activation_cache = TTLCache(maxsize=1024, ttl=ACTIVATION_TTL_SECOND)

        # key: user_id, value: True (to indicate the entry exists; can be any dummy value)
        self.resend_cooldown = TTLCache(maxsize=1024, ttl=RESEND_COOLDOWN_TTL_SECOND)

        with open('/var/www/ictrl/application/resources/activation_email_template.html', 'r') as f:
            self.activation_email_body_template = f.read()

        class User(db.Model):
            __table_args__ = {"schema": "ictrl"}

            id = db.Column(db.Integer, primary_key=True)
            sessions = db.relationship('Session', backref='user', lazy=True)

            username = db.Column(db.String, unique=True, nullable=False)

            @validates('username')
            def validate_username(self, key, username):
                assert re.match("^[A-Za-z0-9_-]+$", username), \
                    'User name should contain only letters, numbers, underscores and dashes'
                return username.lower()

            # this field is for the hashed passwords
            # for the password requirements verifications, please see "self.add_user"
            password = db.Column(db.String, nullable=False)

            email = db.Column(db.String, unique=True, nullable=False)

            @validates('email')
            def validate_email(self, key, email):
                email = email.lower()

                assert re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email), \
                    f'Invalid email address: "{email}"'

                # FIXME: remove this utoronto mail restriction in the future
                assert email.endswith('utoronto.ca'), "Currently, only Uoft emails are supported"

                return email

            activation_type = db.Column(db.Integer, nullable=False, default=ActivationType.NOT_ACTIVATED)

        class Session(db.Model):
            __table_args__ = {"schema": "ictrl"}

            id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            user_id = db.Column(db.Integer, db.ForeignKey('ictrl.user.id'), nullable=False)

            host = db.Column(db.String, nullable=False)
            username = db.Column(db.String, nullable=False)
            private_key = db.Column(db.Text, nullable=True)

        self.User = User
        self.Session = Session

        # db.drop_all()
        db.engine.execute("CREATE SCHEMA IF NOT EXISTS ictrl;")
        db.create_all()

    def login(self, username, password):
        username = username.lower()
        password_bytes = password.encode('ascii')

        user = self.User.query.filter_by(username=username).first()
        if user is None:
            abort(403, 'ACCOUNT_WRONG_USERNAME')

        if user.activation_type == ActivationType.NOT_ACTIVATED:
            abort(401, 'ACCOUNT_NOT_ACTIVATED')

        hashed_password_bytes = user.password.encode('ascii')
        if not bcrypt.checkpw(password_bytes, hashed_password_bytes):
            abort(403, 'ACCOUNT_WRONG_PASSWORD')

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
        flask_session.pop('userid', None)

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
                "username": session.username
            }

        return _profile

    def add_user(self, username, password, email):
        password_ok, password_reason = validate_password(password)
        if not password_ok:
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
                abort(422, 'ACCOUNT_DUPLICATE_USERNAME')
            elif 'user_email_key' in error_info:
                abort(422, 'ACCOUNT_DUPLICATE_EMAIL')

            abort(403, e)

        return True, ''

    def activate_user(self, userid, code):
        cached_code = self.activation_cache.get(userid, None)

        if not cached_code:
            return False
        elif cached_code == code:
            user = self.User.query.filter_by(id=userid).first()
            if user is None:
                abort(403, f'Cannot find any matching user with userid={userid}')

            user.activation_type = ActivationType.NORMAL_USER
            self.save_profile()

            return True

        return False

    def get_user(self):
        if 'userid' not in flask_session:
            abort(403, 'You are not logged in')
        userid = flask_session['userid']

        user = self.User.query.filter_by(id=userid).first()
        if user is None:
            abort(403, 'Cannot find any matching record')

        return user

    def add_session(self, host, username, conn=None):
        user = self.get_user()
        try:
            session = self.Session(id=uuid.uuid4(), user=user, host=host, username=username)

            if conn is not None:
                key_file_obj = StringIO()
                status, reason = conn.save_keys(key_file_obj=key_file_obj,
                                                public_key_comment=f'icrtl-session.id')
                if not status:
                    return status, reason

                clear_private_key = key_file_obj.getvalue().encode('ascii')
                f = Fernet(flask_session['session_crypt_key'])
                session.private_key = f.encrypt(clear_private_key).decode('ascii')

            self.db.session.add(session)
            self.save_profile()
        except AssertionError as e:
            abort(403, e)
        except sqlalchemy.exc.IntegrityError as e:
            abort(403, e)

        return True, ''

    def get_session(self, session_id):
        if 'userid' not in flask_session:
            abort(403, 'You are not logged in')
        userid = flask_session['userid']

        return self.Session.query.filter_by(id=session_id, user_id=userid).first()

    def delete_session(self, session_id):
        session = self.get_session(session_id)
        if session is None:
            return False, f'failed: session {session_id} does not exist'

        self.db.session.delete(session)
        self.save_profile()

        return True, ''

    def change_host(self, session_id, new_host):
        session = self.get_session(session_id)
        if session is None:
            return False, f'failed: session {session_id} does not exist'

        session.host = new_host
        self.save_profile()

        return True, ''

    def save_profile(self):
        self.db.session.commit()

    def get_session_info(self, session_id):
        session = self.get_session(session_id)
        if session is None:
            return None, None, None

        f = Fernet(flask_session['session_crypt_key'])
        crypt_key_bytes = session.private_key.encode('ascii')
        clear_private_key = f.decrypt(crypt_key_bytes).decode('ascii')

        return session.host, session.username, None, clear_private_key

    def send_activation_email(self, username):
        user = self.User.query.filter_by(username=username).first()
        if user is None:
            abort(403, f'Cannot find any matching user with username={username}')
        elif self.resend_cooldown.get(str(user.id), None):
            abort(429, f'Too soon to resend. Please check your email junk box or try again in '
                       f'{RESEND_COOLDOWN_TTL_SECOND} seconds. ')

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

        return True
