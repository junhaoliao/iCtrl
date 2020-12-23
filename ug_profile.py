import base64
import json

import exceptions
from path_names import *


class UG_Profile():
    instantiated = False

    def __new__(cls, *args, **kwargs):
        # to prevent misuse of the class
        if cls.instantiated:
            raise exceptions.MisuseError("class %s has been instantiated. Misuse of constructor. " % cls.__name__)

        return super(UG_Profile, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        self.loaded = False
        self.vnc_passwd_exist = False
        self.username = None
        self.ug_passwd = None
        self.last_srv = None

        self.__class__.instantiated = True

    def load_profile(self):
        if self.loaded:
            raise exceptions.MisuseError("Profile already loaded. Misuse of load_profile(). ")

        self.vnc_passwd_exist = os.path.exists(VNC_PASSWD_PATH)

        try:
            print("Profile loading... ")
            with open(PROFILE_FILE_PATH, "r") as infile:
                json_data = json.load(infile)
                self.username = json_data['saved_username']
                obfuscated_passwd = json_data['saved_password']
                self.ug_passwd = base64.b64decode(obfuscated_passwd).decode('ascii')
                self.last_srv = json_data['last_srv']
                self.loaded = True
                print("Profile loaded with username: ", self.username)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.loaded = False
            print("Profile not loaded. ")

    def set_profile(self, username, ug_password, last_srv):
        self.username = username
        self.ug_passwd = ug_password
        self.last_srv = last_srv

        self.loaded = True

    def save_profile(self):
        try:
            with open(PROFILE_FILE_PATH, 'w') as outfile:
                json_data = json.dumps(
                    {
                        'saved_username': self.username,
                        'saved_password': base64.b64encode(self.ug_passwd.encode('ascii')).decode('ascii'),
                        'last_srv': self.last_srv,
                    }
                )
                outfile.write(json_data)
        except Exception:
            # need to handle any write permission issues, once observed
            raise Exception
