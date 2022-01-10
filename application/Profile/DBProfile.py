import os
import re
import uuid
from io import StringIO

import bcrypt
import sqlalchemy
from flask import session as flask_session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates

from ..email_utils import send_email

from cachetools import TTLCache

ACTIVATION_TTL_SECOND = 1800
RESEND_TTL_SECOND = 30


class LowerCaseText(types.TypeDecorator):
    impl = types.String

    def process_bind_param(self, value, dialect):
        return value.lower()


class DBProfile:

    def __init__(self, app):
        db_passwd = os.environ['DBPASSWD']
        db_address = os.environ['DBADDR']
        app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{db_passwd}@{db_address}"

        self.db = db = SQLAlchemy(app)
        self.salt = bcrypt.gensalt()

        self.activation_cache = TTLCache(maxsize=1024, ttl=ACTIVATION_TTL_SECOND)
        self.resend_cache = TTLCache(maxsize=1024, ttl=RESEND_TTL_SECOND)

        with open('application/resources/activation_email_template.html', 'r') as f:
            self.activation_email_body_template = f.read()

        class User(db.Model):
            __table_args__ = {"schema": "ictrl"}

            id = db.Column(db.Integer, primary_key=True)
            sessions = db.relationship('Session', backref='user', lazy=True)

            username = db.Column(LowerCaseText, unique=True, nullable=False)

            @validates('username')
            def validate_username(self, key, username):
                assert re.match("^[A-Za-z0-9_-]+$", username), \
                    'User name should contain only letters, numbers, underscores and dashes'
                return username

            password = db.Column(db.String, nullable=False)

            email = db.Column(db.String, unique=True, nullable=False)

            @validates('email')
            def validate_email(self, key, email):
                assert re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email), \
                    f'Invalid email address: "{email}"'
                return email

            # provide different services depending on the type:
            # 0: not activated (first time email not verified)
            # 1: normal user
            # more to be added...
            activation_type = db.Column(db.Integer, nullable=False, default=0)

        class Session(db.Model):
            __table_args__ = {"schema": "ictrl"}

            id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
            user_id = db.Column(db.Integer, db.ForeignKey('ictrl.user.id'), nullable=False)

            host = db.Column(db.String, nullable=False)
            username = db.Column(db.String, nullable=False)
            private_key = db.Column(db.Text, nullable=True)

        self.tables = {
            'User': User,
            'Session': Session
        }

        # db.drop_all()
        db.engine.execute("CREATE SCHEMA IF NOT EXISTS ictrl;")
        db.create_all()

    def login(self, username, password):
        User = self.tables['User']

        password = password.encode('ascii')

        user = User.query.filter_by(username=username).first()
        if user is None:
            abort(403, 'Cannot find any matching record')

        hashed_password = user.password.encode('ascii')
        if not bcrypt.checkpw(password, hashed_password):
            abort(403, 'Cannot find any matching record')

        flask_session.clear()
        flask_session['userid'] = user.id

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
        User = self.tables['User']

        # hash the password before storing
        password = password.encode('ascii')
        hashed_password = bcrypt.hashpw(password, self.salt).decode('ascii')

        try:
            user = User(username=username, password=hashed_password, email=email)
            self.db.session.add(user)
            self.save_profile()

            code = uuid.uuid4()
            self.activation_cache[user.id] = code
            self.send_activation_email(email, user.id, code)

        except AssertionError as e:
            abort(403, e)
        except sqlalchemy.exc.IntegrityError as e:
            abort(403, e)

        return True, ''

    def send_activation_email(self, email):
        sender_email = 'notifications.ictrl@gmail.com'
        sender_password = 'iCtrl2022'

        User = self.tables['User']
        user = User.query.filter_by(email=email).first()
        if user is None:
            abort(403, 'Cannot find any matching record')
        if self.resend_cache.get(str(user.id), None):
            abort(429, 'Too soon to resend')
        code = uuid.uuid4()
        self.activation_cache[str(user.id)] = str(code)
        self.resend_cache[str(user.id)] = True
        body = self.activation_email_body_template.format(userid=user.id,
                                                          code=code,
                                                          expire_min=int(ACTIVATION_TTL_SECOND / 60))
        send_email(sender_email, sender_password, email, 'Activate Your iCtrl Account', body)
        return True

    def activate_user(self, userid, code):
        cached_code = self.activation_cache.get(userid, None)
        if not cached_code:
            return False
        if cached_code == code:
            User = self.tables['User']
            user = User.query.filter_by(id=userid).first()
            if user is None:
                abort(403, 'Cannot find any matching record')
            user.activation_type = 1
            self.save_profile()
            return True
        return False

    def get_user(self):
        User = self.tables['User']

        if 'userid' not in flask_session:
            abort(403, 'You are not logged in')
        userid = flask_session['userid']

        user = User.query.filter_by(id=userid).first()
        if user is None:
            abort(403, 'Cannot find any matching record')

        return user

    def add_session(self, host, username, conn=None):
        Session = self.tables['Session']

        user = self.get_user()
        try:
            session = Session(id=uuid.uuid4(), user=user, host=host, username=username)

            if conn is not None:
                key_file_obj = StringIO()
                status, reason = conn.save_keys(key_file_obj=key_file_obj,
                                                public_key_comment=f'icrtl-session.id')
                if not status:
                    return status, reason

                session.private_key = key_file_obj.getvalue()

            self.db.session.add(session)
            self.save_profile()
        except AssertionError as e:
            abort(403, e)
        except sqlalchemy.exc.IntegrityError as e:
            abort(403, e)

        return True, ''

    def get_session(self, session_id):
        Session = self.tables['Session']

        if 'userid' not in flask_session:
            abort(403, 'You are not logged in')
        userid = flask_session['userid']

        return Session.query.filter_by(id=session_id, user_id=userid).first()

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

        return session.host, session.username, None, session.private_key
