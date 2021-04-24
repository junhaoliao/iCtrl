import os
import sys
from typing import Any

from ug_profile.UGConnProfile import *
from paths import *


# TODO: check argument verification and assignment order

class UGUserProfile:
    """ User Profile that stores all opened session and user settings
    >>> USER_PROFILE_PATH = "/Users/junhao/PycharmProjects/PyMotron/profile/user_profile.json"
    >>> TEMP_PRIVATE_KEY_PATH = "/Users/junhao/PycharmProjects/PyMotron/profile/id_rsa"
    >>> TEMP_PASSWD_PATH = "/Users/junhao/PycharmProjects/PyMotron/profile/id_rsa"
    >>> user_profile = UGUserProfile()
    >>> # this class is a singleton
    >>> UGUserProfile()
    Traceback (most recent call last):
        ...
    ValueError: class UGUserProfile has been instantiated. Misuse of constructor.
    >>> user_profile["version"]
    1
    >>> user_profile.add_new_session("EECG1","UG")
    Traceback (most recent call last):
        ...
    ValueError: UGUserProfile: add_new_session: Invalid conn_profile=UG
    >>> user_profile.add_new_session("EECG1","eecg")
    >>> user_profile.add_new_session("EECG1","eecg")
    Traceback (most recent call last):
        ...
    ValueError: UGUserProfile: add_new_session: Already have session_name=EECG1
    >>> user_profile.modify_session("ecf","liaojunh", "")
    Traceback (most recent call last):
        ...
    IndexError: UGUserProfile: modify_session: Invalid session_name=ecf
    >>> user_profile.modify_session("EECG1", "liaojunh", "non-existing-server")
    Traceback (most recent call last):
        ...
    ValueError: UGUserProfile: modify_session: Invalid last_server=non-existing-server
    >>> user_profile.modify_session("EECG1", "liaojunh", "ug250.eecg.toronto.edu", private_key_path=TEMP_PRIVATE_KEY_PATH,
    ...     vnc_passwd_path=TEMP_PASSWD_PATH)
    >>> user_profile["sessions"]["EECG1"] # doctest:+ELLIPSIS
    {'conn_profile': 'eecg', 'last_server': 'ug250.eecg.toronto.edu', 'username': 'liaojunh', \
'private_key_path': '...', 'vnc_passwd_path': '...'}
    >>> user_profile.add_new_session("ECF1","ecf")
    >>> user_profile.modify_session("ECF1", "liaojunh", "remote.ecf.utoronto.ca")
    >>> user_profile["sessions"]["ECF1"]
    {'conn_profile': 'ecf', 'last_server': 'remote.ecf.utoronto.ca', 'username': 'liaojunh', \
'private_key_path': '', 'vnc_passwd_path': ''}
    >>> user_profile.save_profile(USER_PROFILE_PATH)
    >>> user_profile.load_profile("non_existing_path") # the profile should be reset after this call
    UGUserProfile loading...
    UGUserProfile: load_profile: [Errno 2] No such file or directory: 'non_existing_path'
    Unable to load the user profile. Using the default profile instead.
    >>> user_profile["non-existing-key"]
    Traceback (most recent call last):
        ...
    KeyError: 'non-existing-key'
    >>> user_profile["viewer"]
    'TigerVNC'
    >>> user_profile.change_viewer("non-existing-viewer")
    Traceback (most recent call last):
        ...
    NotImplementedError: UGUserProfile: change_viewer: non-existing-viewer not supported.
    >>> user_profile.change_viewer("RealVNC")
    >>> user_profile["viewer"]
    'RealVNC'
    >>> user_profile["last_session"]
    ''
    >>> user_profile["sessions"]
    {}
    >>> user_profile.load_profile(USER_PROFILE_PATH)
    UGUserProfile loading...
    >>> user_profile["viewer"]
    'TigerVNC'
    >>> user_profile["last_session"]
    'ECF1'
    >>> user_profile["sessions"] # doctest:+ELLIPSIS
    {'EECG1': {'conn_profile': 'eecg', 'last_server': 'ug250.eecg.toronto.edu', 'username': 'liaojunh', \
'private_key_path': '...', 'vnc_passwd_path': '...'}, \
'ECF1': {'conn_profile': 'ecf', 'last_server': 'remote.ecf.utoronto.ca', 'username': 'liaojunh', \
'private_key_path': '', 'vnc_passwd_path': ''}}
    >>> user_profile.query_sessions() # doctest:+ELLIPSIS
    {'EECG1': {'servers': ['ug51.eecg.toronto.edu', ..., 'ug251.eecg.toronto.edu'], \
'last_server': 'ug250.eecg.toronto.edu', 'username': 'liaojunh', 'private_key': True, 'vnc_manual': True, \
'vnc_passwd': True}, 'ECF1': {'servers': ['remote.ecf.utoronto.ca', ...], \
'last_server': 'remote.ecf.utoronto.ca', 'username': 'liaojunh', 'private_key': False, 'vnc_manual': False, \
'vnc_passwd': False}}
    """
    version = 1  # in case the schema changes in the future
    instantiated = False

    _supported_viewers = ["TigerVNC", "RealVNC"]

    _empty_session = {
        "conn_profile": "",
        "last_server": "",
        "username": "",
        "private_key_path": "",
        "vnc_passwd_path": ""
    }

    _empty_user_profile = {
        "version": version,
        "viewer": "TigerVNC",
        "sessions": {},
        "last_session": ""
    }

    def __new__(cls, *args, **kwargs):
        # to prevent misuse of the class
        if cls.instantiated:
            raise ValueError("class %s has been instantiated. Misuse of constructor." % cls.__name__)

        return super(UGUserProfile, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        self._profile = copy.deepcopy(UGUserProfile._empty_user_profile)

        self._conn_profiles = {}
        for file_name in os.listdir(CONN_PROFILE_PATH):
            if file_name.endswith(".json"):
                conn_profile = UGConnProfile()
                conn_profile.load_profile(CONN_PROFILE_PATH + file_name)
                self._conn_profiles[file_name[:-5]] = conn_profile

        UGUserProfile.instantiated = True

    def __setitem__(self, key, value):
        self._profile[key] = value

    def __getitem__(self, key):
        return self._profile[key]

    def load_session(self, session):
        """
         _empty_session = {
            "name": "",
            "conn_profile": "",
            "last_server": "",
            "username": "",
            "private_key_path": "",
            "vnc_passwd_path": ""
        }
        """
        loaded_session = copy.deepcopy(UGUserProfile._empty_session)

        # load the connection profile
        # TODO: recheck whether we should handle this gracefully
        loaded_session["conn_profile"] = session["conn_profile"]
        conn_profile = self._conn_profiles[session["conn_profile"]]

        # load the last used server
        # TODO: recheck whether we should handle this gracefully
        if session["last_server"] not in conn_profile["servers"]:
            loaded_session["last_server"] = ""
        else:
            loaded_session["last_server"] = session["last_server"]

        # load the username
        loaded_session["username"] = session["username"]

        # load the SSH private key path
        if not os.path.exists(session["private_key_path"]):
            # TODO: recheck whether we should handle this gracefully
            # raise FileNotFoundError(f"UGUserProfile: Unable to find private_key_path="
            #                         f"{session['private_key_path']}")
            loaded_session["private_key_path"] = ""
        else:
            loaded_session["private_key_path"] = session["private_key_path"]

            # load the VNC passwd file path
            if not os.path.exists(session["vnc_passwd_path"]):
                # TODO: recheck whether we should handle this gracefully
                # raise FileNotFoundError(f"UGUserProfile: Unable to find vnc_passwd_path="
                #                         f"{session['vnc_passwd_path']}")
                loaded_session["vnc_passwd_path"] = ""
            else:
                loaded_session["vnc_passwd_path"] = session["vnc_passwd_path"]
        return loaded_session

    def load_profile(self, file_path):
        print("UGUserProfile loading...")
        self._profile = copy.deepcopy(UGUserProfile._empty_user_profile)
        # self.eecg_vnc_passwd_exist = os.path.exists(VNC_PASSWD_PATH)

        try:
            with open(file_path, "r") as infile:
                json_data = json.load(infile)

                # TODO: might attempt profile recovery even if some of the parameters are incorrect
                # if the version doesn't match then stop loading
                if "version" not in json_data or json_data["version"] != UGUserProfile.version:
                    raise ValueError("UGUserProfile: Version info not found or mismatch in the profile.")

                # make sure the profile file is not modified in an attempt to crash the script
                if json_data["viewer"] not in UGUserProfile._supported_viewers:
                    raise ValueError(f"UGUserProfile: Viewer {json_data['viewer']} not supported.")
                self["viewer"] = json_data["viewer"]

                for session_name, session in json_data["sessions"].items():
                    # TODO: check name duplicate: might not be necessary if JSON already handles that
                    # TODO: should definitely attempt recovery here
                    loaded_session = self.load_session(session)
                    self["sessions"][session_name] = loaded_session

                if json_data["last_session"] not in self["sessions"]:
                    raise IndexError(f"UGUserProfile: Invalid last_session={json_data['last_session']}")
                self["last_session"] = json_data["last_session"]

        except Exception as e:
            self._profile = copy.deepcopy(UGUserProfile._empty_user_profile)
            print("UGUserProfile: load_profile:", e)
            # raise e
            # TODO: print the profile path for debugging
            print("Unable to load the user profile. Using the default profile instead.")

    def add_new_session(self, session_name, conn_profile):
        # TODO: should support renaming the sessions later
        """
         _empty_session = {
            "conn_profile": "",
            "last_server": "",
            "username": "",
            "private_key_path": "",
            "vnc_passwd_path": ""
        }
        """
        if session_name in self["sessions"]:
            raise ValueError(f"UGUserProfile: add_new_session: Already have session_name={session_name}")

        new_session = copy.deepcopy(UGUserProfile._empty_session)

        if conn_profile not in self._conn_profiles:
            raise ValueError(f"UGUserProfile: add_new_session: Invalid conn_profile={conn_profile}")
        new_session["conn_profile"] = conn_profile

        self["sessions"][session_name] = new_session

    # TODO: support renaming a session

    def modify_session(self, session_name, username, last_server, private_key_path=None, vnc_passwd_path=None):
        if session_name not in self["sessions"]:
            raise IndexError(f"UGUserProfile: modify_session: Invalid session_name={session_name}")

        # TODO: check whether we should have a dedicated function to update the last session
        self["last_session"] = session_name

        session: Any = self["sessions"][session_name]
        session["username"] = username

        if last_server not in self._conn_profiles[session["conn_profile"]]["servers"]:
            raise ValueError(f"UGUserProfile: modify_session: Invalid last_server={last_server}")
        session["last_server"] = last_server

        # FIXME: recheck whether the private key should be optional
        if private_key_path is not None:
            # TODO: check whether the private_key_path is valid
            session["private_key_path"] = private_key_path

        # FIXME: recheck whether the vnc_passwd_path key should be optional
        if vnc_passwd_path is not None:
            # TODO: check whether the conn_profile supports vnc_manual
            # TODO: check whether the vnc_passwd_path is valid
            session["vnc_passwd_path"] = vnc_passwd_path

    def change_viewer(self, viewer):
        if viewer not in UGUserProfile._supported_viewers:
            raise NotImplementedError(f"UGUserProfile: change_viewer: {viewer} not supported.")
        self["viewer"] = viewer

    def save_profile(self, file_path):
        try:
            with open(file_path, 'w') as outfile:
                json_data = json.dumps(self._profile, indent=4)
                outfile.write(json_data)
        except Exception:
            # need to handle any write permission issues, once observed
            raise Exception

    def query_sync(self):
        """
            "sessions":
            {
                "session_name":
                {
                    "profile": "eecg"
                    "last_server": "ug250.eecg.toronto.edu",
                    "username":"",
                    "private_key":false,
                    "vnc_passwd": false
                },
                ...
            },
            "profiles":
            {
                ...
            },
            "last_session": "session_name"
        """
        queried_sessions_dict = {}
        for session_name, session in self["sessions"].items():
            session: Dict
            queried_sessions_dict[session_name] = {
                "profile": session["conn_profile"],
                "last_server": session["last_server"],
                "username": session["username"],
                "private_key": (session["private_key_path"] != ""),
                "vnc_passwd": (session["vnc_passwd_path"] != "")
            }

        return {
            "sessions": queried_sessions_dict,
            "profiles": self.query_profiles(),
            "last_session": self["last_session"]
        }

    def query_profiles(self):
        """
        {
            "eecg":
            {
                "vnc_manual": false
                "servers":[
                    "ug250.eecg.toronto.edu",
                    "ug251.eecg.toronto.edu",
                    ...
                ],
            },
            "ecf":
            {
                "vnc_manual": true,
                "servers": [...]
            }
        }
        """
        # TODO: add test cases
        queried_profiles_dict = {}
        for conn_profile_name, conn_profile in self._conn_profiles.items():
            print(conn_profile_name, conn_profile)
            queried_profiles_dict[conn_profile_name] = {
                "vnc_manual": conn_profile["vnc_manual"],
                "servers": conn_profile["servers"]
            }

        return queried_profiles_dict

