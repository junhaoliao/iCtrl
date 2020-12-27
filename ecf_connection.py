import paramiko

import exceptions
import ug_connection


class ECFConnection(ug_connection.UGConnection):
    LOCAL_PORT = 2000
    REMOTE_PORT = 1000
    instantiated = False

    def __new__(cls, *args, **kwargs):
        # to prevent misuse of the class
        if cls.instantiated:
            raise exceptions.MisuseError("class %s has been instantiated. Misuse of constructor. " % cls.__name__)

        return super(ECFConnection, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        super().__init__()

        ECFConnection.instantiated = True

    def __del__(self):
        self.disconnect()

        # may not need to set this as ECFConnection.__del__() should never be called
        ECFConnection.instantiated = False

    def connect(self, username, ecf_passwd, **kwargs):
        try:
            super().connect("remote.ecf.utoronto.ca", username=username, passwd=ecf_passwd)
        except OSError:
            raise exceptions.NetworkError(
                "ECF Server remote.ecf.utoronto.ca unreachable. \n"
                "Please check you network or try again later. ")

        except paramiko.ssh_exception.AuthenticationException:
            raise exceptions.SSHAuthError("SSH Authentication Failed. \n"
                                          "Please check your username or ECF password. ")

    def disconnect(self):
        super().disconnect()

    def create_vnc_tunnel(self):
        if not self.connected:
            raise exceptions.MisuseError("The client is not yet connected. Misuse of function \"create_vnc_tunnel()\"")

        super().create_forward_tunnel(ECFConnection.LOCAL_PORT, ECFConnection.REMOTE_PORT)
