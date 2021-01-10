import base64
import copy
import json
import datetime

import exceptions
from path_names import *


class UGProfile:
    version = 2  # in case the schema changes in the future
    instantiated = False
    _empty_profile = {
        "version": version,
        "last_checked_update": datetime.datetime.now().isoformat(),
        "last_lab": "EECG",
        "EECG": {
            "loaded": False,
            "username": "",
            "passwd": "",
            "last_srv": None
        },
        "ECF": {
            "loaded": False,
            "username": "",
            "passwd": ""
        }
    }

    def __new__(cls, *args, **kwargs):
        # to prevent misuse of the class
        if cls.instantiated:
            raise exceptions.MisuseError("class %s has been instantiated. Misuse of constructor. " % cls.__name__)

        return super(UGProfile, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        self._profile = copy.deepcopy(UGProfile._empty_profile)
        self.eecg_vnc_passwd_exist = False

        UGProfile.instantiated = True

    def __setitem__(self, key, value):
        self._profile[key] = value

    def __getitem__(self, key):
        return self._profile[key]

    def load_profile(self):
        print("Profile loading... ")
        self._profile = copy.deepcopy(UGProfile._empty_profile)
        self.eecg_vnc_passwd_exist = os.path.exists(VNC_PASSWD_PATH)

        try:
            with open(PROFILE_FILE_PATH, "r") as infile:
                json_data = json.load(infile)

                if "version" not in json_data or json_data["version"] != UGProfile.version:
                    print("Both EECG and ECF Profile not loaded. ")
                    return

                # make sure the profile file is not modified in an attempt to crash the script
                #  let the broad exception handler handle the error
                self["last_checked_update"] = datetime.datetime.fromisoformat(
                    json_data["last_checked_update"]).isoformat()
                self["last_lab"] = json_data["last_lab"]
                if self["last_lab"] not in ("EECG", "ECF"):
                    raise KeyError

                if not json_data["EECG"]["loaded"]:
                    print("EECG Profile not loaded. ")
                else:
                    self["EECG"]["username"] = json_data["EECG"]["username"]
                    eecg_obfuscated_passwd = json_data["EECG"]["passwd"]
                    self["EECG"]["passwd"] = base64.b64decode(eecg_obfuscated_passwd).decode("ascii")
                    self["EECG"]["last_srv"] = json_data["EECG"]["last_srv"]
                    self["EECG"]["loaded"] = True
                    print("EECG Profile loaded with username: ", self["EECG"]["username"])

                if not json_data["ECF"]["loaded"]:
                    print("ECF Profile not loaded. ")
                else:
                    self["ECF"]["username"] = json_data["ECF"]["username"]
                    ecf_obfuscated_passwd = json_data["ECF"]["passwd"]
                    self["ECF"]["passwd"] = base64.b64decode(ecf_obfuscated_passwd).decode('ascii')
                    self["ECF"]["loaded"] = True
                    print("ECF Profile loaded with username: ", self["ECF"]["username"])

        except Exception:
            self._profile = copy.deepcopy(UGProfile._empty_profile)
            print("Both EECG and ECF Profile not loaded. ")

    def set_eecg_profile(self, last_srv, username, password):
        self["EECG"]["last_srv"] = last_srv
        self["EECG"]["username"] = username
        self["EECG"]["passwd"] = password

        self["EECG"]["loaded"] = True

    def set_ecf_profile(self, username, password):
        self["ECF"]["username"] = username
        self["ECF"]["passwd"] = password

        self["ECF"]["loaded"] = True

    def save_profile(self, last_lab):
        if type(last_lab) is not str or last_lab not in ("EECG", "ECF"):
            raise exceptions.MisuseError("last_lab should be one of 'EECG' or 'ECF'")

        self["last_lab"] = last_lab
        try:
            with open(PROFILE_FILE_PATH, 'w') as outfile:
                profile_dict = copy.deepcopy(self._profile)
                profile_dict["last_checked_update"] = datetime.datetime.now().isoformat()
                profile_dict["EECG"]["passwd"] = base64.b64encode(self["EECG"]["passwd"].encode('ascii')).decode(
                    'ascii')
                profile_dict["ECF"]["passwd"] = base64.b64encode(self["ECF"]["passwd"].encode('ascii')).decode('ascii')

                json_data = json.dumps(profile_dict, indent=4)
                outfile.write(json_data)
        except Exception:
            # need to handle any write permission issues, once observed
            raise Exception
