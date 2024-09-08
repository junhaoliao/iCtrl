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
import copy
import json
import logging
import uuid

from application.paths import *
from .Profile import Profile

_PROFILE_VERSION = 1  # in case the schema changes in the future

_EMPTY_SESSION = {
    "host": "",
    "username": ""
}

_EMPTY_USER_PROFILE = {
    "version": _PROFILE_VERSION,
    "sessions": {},
}

logger = logging.getLogger(__name__)


class LocalProfile(Profile):
    def login(self, username, password):
        not_implemented_error = f'Method {__name__} should not be invoke from {__class__}'
        logger.error(not_implemented_error)
        raise NotImplementedError(not_implemented_error)

    @staticmethod
    def logout():
        not_implemented_error = f'Method {__name__} should not be invoke from {__class__}'
        logger.error(not_implemented_error)
        raise NotImplementedError(not_implemented_error)

    def add_user(self, username, password, email):
        not_implemented_error = f'Method {__name__} should not be invoke from {__class__}'
        logger.error(not_implemented_error)
        raise NotImplementedError(not_implemented_error)

    def activate_user(self, userid, code):
        not_implemented_error = f'Method {__name__} should not be invoke from {__class__}'
        logger.error(not_implemented_error)
        raise NotImplementedError(not_implemented_error)

    def send_activation_email(self, username):
        not_implemented_error = f'Method {__name__} should not be invoke from {__class__}'
        logger.error(not_implemented_error)
        raise NotImplementedError(not_implemented_error)

    def __init__(self):
        self._profile = copy.deepcopy(_EMPTY_USER_PROFILE)
        try:
            logger.debug(f"Attempting to open file: {USER_PROFILE_PATH}")
            with open(USER_PROFILE_PATH, "r") as infile:
                json_data = json.load(infile)

                if "version" not in json_data or json_data["version"] != _PROFILE_VERSION:
                    value_error = "LocalProfile: Version info not found or mismatch in the profile."
                    logger.error(value_error)
                    raise ValueError(value_error)

                self._profile["sessions"] = json_data["sessions"]

        except Exception as e:
            self._profile = copy.deepcopy(_EMPTY_USER_PROFILE)
            logger.error(f"LocalProfile: Error loading profile: {e}")
            logger.warning("Unable to load the user profile. Using the default profile instead.")

    def query(self):
        logger.info("querying profile")
        return self._profile

    def add_session(self, host, username, conn=None):
        session = copy.deepcopy(_EMPTY_SESSION)

        session_id = uuid.uuid4().hex
        self._profile["sessions"][session_id] = session
        session["host"] = host
        session["username"] = username

        if conn is not None:
            this_private_key_path = os.path.join(PRIVATE_KEY_PATH, session_id)
            status, reason = conn.save_keys(key_filename=this_private_key_path,
                                            public_key_comment=this_private_key_path)
            if not status:
                logger.warning(f"Failed to save RSA SSH private key in {this_private_key_path}")
                return status, reason

        self.save_profile()

        logger.info(f"Successfully saved RSA SSH private key")
        return True, ''

    def delete_session(self, session_id):
        if session_id not in self._profile['sessions']:
            logger.error(f"Cannot delete session {session_id}, session does not exist")
            return False, f'failed: session {session_id} does not exist'

        try:
            os.remove(os.path.join(PRIVATE_KEY_PATH, session_id))
        except FileNotFoundError:
            logger.error('Not valid SSH key found for deletion')

        self._profile['sessions'].pop(session_id)
        self.save_profile()

        logger.info(f'Successfully deleted session {session_id}')

        return True, ''

    def change_host(self, session_id, new_host):
        if session_id not in self._profile['sessions']:
            logger.error(f'Cannot change host, session {session_id} does not exist')
            return False, f'failed: session {session_id} does not exist'

        self._profile["sessions"][session_id]['host'] = new_host
        self.save_profile()

        logger.info(f"Successfully changed host for session {session_id} to new host {new_host}")

        return True, ''

    def save_profile(self):
        try:
            with open(USER_PROFILE_PATH, 'w') as outfile:
                json_data = json.dumps(self._profile, indent=4)
                outfile.write(json_data)
        except Exception as e:
            # need to handle any write permission issues, once observed
            raise e

    def get_session_info(self, session_id):
        if session_id not in self._profile['sessions']:
            logger.error(f"Cannot retrieve session {session_id}, session does not exist")
            return None, None, None, None, None

        host = self._profile['sessions'][session_id]['host']
        username = self._profile['sessions'][session_id]['username']
        this_private_key_path = os.path.join(PRIVATE_KEY_PATH, session_id)
        if 'nickname' in self._profile['sessions'][session_id]:
            nickname = self._profile['sessions'][session_id]['nickname']
        else:
            nickname = None

        logger.info(f"Successfully retrieved session info for {session_id}")

        return host, username, this_private_key_path, None, nickname

    def set_session_nickname(self, session_id, nickname):
        if session_id not in self._profile['sessions']:
            logger.error(f"Cannot retrieve session {session_id}, session does not exist")
            return False, f'failed: session {session_id} does not exist'

        if len(nickname) > 8:
            logger.debug(f"Entered nickname must be under 8 characters")
            return False, "Entered nickname is too long"

        if nickname == "":
            # it is a delete request
            if 'nickname' in self._profile['sessions'][session_id]:
                self._profile['sessions'][session_id].pop('nickname')
                logger.info(f'Successfully deleted nickname from session {session_id}')
        else:
            # it is an add / update request
            self._profile['sessions'][session_id]['nickname'] = nickname
            logger.info(f'Successfully added/updated nickname for session {session_id}')

        self.save_profile()

        return True, ''

    def set_session_vnc_credentials(self, session_id, credentials):
        if session_id not in self._profile['sessions']:
            logger.error(f"Cannot retrieve session {session_id}, session does not exist")
            return False, f'failed: session {session_id} does not exist'

        if credentials is None:
            # it is a delete request
            if 'vnc_credentials' in self._profile['sessions'][session_id]:
                self._profile['sessions'][session_id].pop('vnc_credentials')
                logger.info(f"Successfully deleted vnc credentials for session {session_id}")
        else:
            # it is an add / update request
            json_str = json.dumps(credentials)
            base64_str = base64.b64encode(json_str.encode('ascii')).decode('ascii')
            self._profile['sessions'][session_id]['vnc_credentials'] = base64_str
            logger.info(f"Successfully added/updated vnc credentials for session {session_id}")

        self.save_profile()

        return True, ''

    def get_session_vnc_credentials(self, session_id):
        if session_id not in self._profile['sessions']:
            logger.error(f"Cannot retrieve session {session_id}, session does not exist")
            return False, f'failed: session {session_id} does not exist'

        logger.info(f"Retrieving vnc credentials for session {session_id}")
        if 'vnc_credentials' in self._profile['sessions'][session_id]:
            json_str = base64.b64decode(self._profile['sessions'][session_id]['vnc_credentials'])
            return True, json.loads(json_str.decode('ascii'))
        else:
            return True, ''

    def get_user(self):
        class DummyUser:
            id = 0

        dummy_user = DummyUser()

        logger.info(f'Returning user: {dummy_user}')
        return dummy_user
