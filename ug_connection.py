import os
import re
import select
import sys
import threading

import paramiko
import socketserver
import exceptions
from path_names import *


class UG_Connection():
    instantiated = False

    def __new__(cls, *args, **kwargs):
        # to prevent misuse of the class
        if cls.instantiated:
            raise exceptions.MisuseError("class %s has been instantiated. Misuse of constructor. " % cls.__name__)

        return super(UG_Connection, cls).__new__(cls, *args, **kwargs)

    def __init__(self):
        self.connected = False
        self.srv_num = None
        self.username = None
        self.ug_passwd = None
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.forward_thread = None
        self.used_ports_lst = []
        self.ports_by_me_lst = []

        self.__class__.instantiated = True

    def connect(self, srv_num, username, ug_passwd):
        if self.connected:
            if self.srv_num != srv_num or self.username != username or self.ug_passwd != ug_passwd:
                self.disconnect()
            else:
                return

        try:
            self.client.connect("ug%d.eecg.toronto.edu" % srv_num, username=username, password=ug_passwd)

        except OSError:
            raise exceptions.NetworkError(
                "UG Server %s unreachable. \n"
                "Please check you network or use another server. " % srv_num)

        except paramiko.ssh_exception.AuthenticationException:
            raise exceptions.SSHAuthError("SSH Authentication Failed. \n"
                                          "Please check your username or UG password. ")

        self.srv_num = srv_num
        self.username = username
        self.ug_passwd = ug_passwd
        self.connected = True

    def disconnect(self):
        print("Disconnecting from previous connection... ")
        self.client.close()
        self.srv_num = None
        self.username = None
        self.ug_passwd = None
        self.used_ports_lst = []
        self.ports_by_me_lst = []
        self.connected = False

    def __del__(self):
        self.disconnect()

        # may not need to set this
        self.__class__.instantiated = False

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
            raise exceptions.MisuseError("The client is not yet connected. Misuse of function \"killall_VNC_servers()\"")

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

        class Handler(socketserver.BaseRequestHandler):
            chain_host = "localhost"
            chain_port = actual_port
            ssh_transport = self.client.get_transport()

            def handle(self):
                try:
                    chan = self.ssh_transport.open_channel(
                        "direct-tcpip",
                        (self.chain_host, self.chain_port),
                        self.request.getpeername(),
                    )
                except Exception as e:
                    raise exceptions.NetworkError(
                        "Incoming request to %s:%d failed: %s"
                        % (self.chain_host, self.chain_port, repr(e))
                    )
                if chan is None:
                    raise exceptions.NetworkError(
                        "Incoming request to %s:%d was rejected by the SSH server."
                        % (self.chain_host, self.chain_port)
                    )

                print(
                    "Connected!  Tunnel open %r -> %r -> %r"
                    % (
                        self.request.getpeername(),
                        chan.getpeername(),
                        (self.chain_host, self.chain_port),
                    )
                )

                try:
                    while True:
                        r, w, x = select.select([self.request, chan], [], [])
                        if self.request in r:
                            data = self.request.recv(1024)
                            if len(data) == 0:
                                break
                            chan.send(data)
                        if chan in r:
                            data = chan.recv(1024)
                            if len(data) == 0:
                                break
                            self.request.send(data)
                except ConnectionResetError or BrokenPipeError:
                    print("Likely TigerVNC Viewer has been closed, or the network is interrupted, "
                          "shutting down")

                peername = self.request.getpeername()
                chan.close()
                self.request.close()
                print("Tunnel closed from %r" % (peername,))
                self.server.shutdown()
                os._exit(0)

        class ForwardServer(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True

        forward_srv = ForwardServer(("", actual_port), Handler)
        self.forward_thread = threading.Thread(target=forward_srv.serve_forever)
        self.forward_thread.start()

    def set_and_save_vnc_passwd(self, vnc_passwd_input):
        reset_cmd_lst = [
            "killall Xtigervnc",
            "rm -rf ~/.vnc",
            "mkdir ~/.vnc",
            "echo '%s'| vncpasswd -f > ~/.vnc/passwd" % vnc_passwd_input,
            "chmod 600 ~/.vnc/passwd",
        ]
        _, stdout, stderr = self.client.exec_command(";".join(reset_cmd_lst))
        print(";".join(reset_cmd_lst))
        for line in stdout:
            print(line)
        for line in stderr:
            print(line)
        _, stdout, _ = self.client.exec_command("echo '%s'| vncpasswd -f" % vnc_passwd_input)
        with open(VNC_PASSWD_PATH, "wb") as vnc_passwd_file:
            vnc_passwd_file.write(stdout.read())