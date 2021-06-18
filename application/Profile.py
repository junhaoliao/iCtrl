import copy
import json
import uuid

from application.paths import *

_PROFILE_VERSION = 1  # in case the schema changes in the future

_EMPTY_SESSION = {
    "host": "",
    "username": ""
}

_EMPTY_USER_PROFILE = {
    "version": _PROFILE_VERSION,
    "viewer": "TigerVNC",
    "sessions": {},
    "last_session": ""
}


class Profile:
    def __init__(self):
        self._profile = copy.deepcopy(_EMPTY_USER_PROFILE)
        try:
            with open(USER_PROFILE_PATH, "r") as infile:
                json_data = json.load(infile)

                if "version" not in json_data or json_data["version"] != _PROFILE_VERSION:
                    raise ValueError("Profile: Version info not found or mismatch in the profile.")

                # FIXME: make sure the profile file is not modified in an attempt to crash the script
                self["viewer"] = json_data["viewer"]
                self["sessions"] = json_data["sessions"]
                self["last_session"] = json_data["last_session"]

        except Exception as e:
            self._profile = copy.deepcopy(_EMPTY_USER_PROFILE)
            print("Profile: load_profile:", e)
            # raise e
            print("Unable to load the user profile. Using the default profile instead.")

    def __setitem__(self, key, value):
        self._profile[key] = value

    def __getitem__(self, key):
        return self._profile[key]

    # TODO: support renaming a session
    def add_session(self, host, username):
        session = copy.deepcopy(_EMPTY_SESSION)

        session_id = uuid.uuid4().hex
        self["sessions"][session_id] = session
        session["host"] = host
        session["username"] = username

        # TODO: check whether we should have a dedicated function to update the last session
        self["last_session"] = session_id
        self.save_profile()

        return session_id

    def change_viewer(self, viewer):
        self["viewer"] = viewer

    def save_profile(self):
        try:
            with open(USER_PROFILE_PATH, 'w') as outfile:
                json_data = json.dumps(self._profile, indent=4)
                outfile.write(json_data)
        except Exception:
            # need to handle any write permission issues, once observed
            raise Exception

    def query(self):
        return self._profile

