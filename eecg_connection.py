import re

import paramiko

import exceptions
import ug_connection
from path_names import *


class EECGConnection(ug_connection.UGConnection):
    instantiated = False

    def __new__(cls, *args, **kwargs):
        # to prevent misuse of the class
        if cls.instantiated:
            raise exceptions.MisuseError("class %s has been instantiated. Misuse of constructor. " % cls.__name__)

        return super(EECGConnection, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        self.used_ports_lst = []
        self.ports_by_me_lst = []

        super().__init__()

        EECGConnection.instantiated = True

    def __del__(self):
        self.disconnect()

        # may not need to set this as EECGConnection.__del__() should never be called
        EECGConnection.instantiated = False

    def connect(self, srv_num, username, eecg_passwd):
        try:
            super().connect("ug%d.eecg.toronto.edu" % srv_num, username=username, passwd=eecg_passwd)
        except OSError:
            raise exceptions.NetworkError(
                "EECG Server %s unreachable. \n"
                "Please check you network or use another server. " % srv_num)

        except paramiko.ssh_exception.AuthenticationException:
            raise exceptions.SSHAuthError("SSH Authentication Failed. \n"
                                          "Please check your username or EECG password. ")

    def disconnect(self):
        self.used_ports_lst = []
        self.ports_by_me_lst = []

        super().disconnect()

    def update_ports(self):
        self.used_ports_lst = []
        self.ports_by_me_lst = []
        if not self.connected:
            raise exceptions.MisuseError("The client is not yet connected. Misuse of function \"update_ports()\"")

        # formulate the vnc port scanning cmd
        scan_ports_cmd_lst = []
        for port in range(5900, 5999):
            scan_ports_cmd_lst.append('sh -c "nc -z -nv 127.0.0.1 ' + str(port) + ' 2>&1" | grep \'open\|succeeded\'')
        scan_ports_cmd = ";".join(scan_ports_cmd_lst)

        # send out the vnc port scanning cmd
        _, stdout, _ = self.client.exec_command(scan_ports_cmd)
        for line in stdout:
            if "open" in line:  # on other machines
                line = line.replace('(UNKNOWN) [127.0.0.1] ', '')  # remove prefix
                line = line.replace(' (?) open', '')  # remove suffix
            elif "succeeded" in line:  # on ug250 and ug251
                line = line.replace('Connection to 127.0.0.1 ', '')  # remove prefix
                line = line.replace(' port [tcp/*] succeeded!', '')  # remove suffix
            else:
                raise exceptions.MisuseError("Unexpected output when scanning vnc ports: %s" % line)

            this_used_port = int(line) - 5900
            if this_used_port <= 0 or this_used_port > 99:
                raise exceptions.MisuseError("Unexpected port number when scanning vnc ports: %d" % this_used_port)
            self.used_ports_lst.append(this_used_port)

            # use the API by vncserver to see what ports are created by me
            _, stdout, _ = self.client.exec_command('vncserver -list')

            for line in stdout:
                this_port_by_me = re.findall(r'\d+', line)
                if len(this_port_by_me) != 0:
                    self.ports_by_me_lst.append(int(this_port_by_me[0]))

    def killall_VNC_servers(self):
        if not self.connected:
            raise exceptions.MisuseError(
                "The client is not yet connected. Misuse of function \"killall_VNC_servers()\"")

        _, _, stderr = self.client.exec_command("killall Xtigervnc")
        for line in stderr:
            print(line)

    def create_vnc_tunnel(self, vnc_port):
        if not self.connected:
            raise exceptions.MisuseError("The client is not yet connected. Misuse of function \"create_vnc_tunnel()\"")
        elif vnc_port > 99 or vnc_port <= 0:
            raise exceptions.MisuseError("VNC port number should be between 1 and 99. ")

        _, _, stderr = self.client.exec_command('vncserver :' + str(vnc_port))
        for line in stderr:
            print('... ' + line.strip('\n'))

        actual_port = 5900 + vnc_port

        super().create_forward_tunnel(actual_port, actual_port)

    def set_and_save_vnc_passwd(self, vnc_passwd_input):
        reset_cmd_lst = [
            # killall -q: don't complain if no process found
            # killall -w: wait until the processes to die then continue to the next cmd
            "killall -q -w Xtigervnc",
            "rm -rf ~/.vnc",
            "mkdir ~/.vnc",
            "echo '%s'| vncpasswd -f > ~/.vnc/passwd" % vnc_passwd_input,
            "chmod 600 ~/.vnc/passwd",
        ]

        _, stdout, stderr = self.client.exec_command(";".join(reset_cmd_lst))
        for line in stdout:
            print(line)
        for line in stderr:
            if "Disk quota exceeded" in line:
                raise exceptions.QuotaError("Quota exceeded. \n"
                                            "Please SSH manually and delete unnecessary files. \n"
                                            "Use \"quota -s\" to verify if you have enough quota. ")
            print(line)

        _, stdout, _ = self.client.exec_command("echo '%s'| vncpasswd -f" % vnc_passwd_input)
        with open(VNC_PASSWD_PATH, "wb") as vnc_passwd_file:
            vnc_passwd_file.write(stdout.read())
