import re
import socket
import threading

import websockify

from application.Connection import Connection
from application.vncpasswd import decrypt_passwd


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('', 0))
        return sock.getsockname()[1]


def websocket_proxy_thread(local_websocket_port, local_vnc_port):
    proxy_server = websockify.LibProxyServer(listen_port=local_websocket_port, target_host='',
                                             target_port=local_vnc_port,
                                             run_once=True)
    proxy_server.serve_forever()
    proxy_server.server_close()


class VNC(Connection):
    def __init__(self):
        self.id = None

        super().__init__()

    def __del__(self):
        super().__del__()

    def connect(self, *args, **kwargs):
        return super().connect(*args, **kwargs)

    def get_vnc_password(self):
        _, _, stdout, stderr = self.exec_command_blocking('xxd -p ~/.vnc/passwd')
        hexdump = stdout.readline()
        if hexdump == '':
            return False, ''
        else:
            return True, decrypt_passwd(bytearray.fromhex(hexdump))

    def reset_vnc_password(self, password):
        reset_cmd_lst = [
            # killall -q: don't complain if no process found
            #         -w: wait until the processes to die then continue to the next cmd
            "killall -q -w Xtigervnc",
            "rm -rf ~/.vnc",
            "mkdir ~/.vnc",
            # TODO: check whether the target has tigervnc installed
            "echo '%s'| tigervncpasswd -f > ~/.vnc/passwd" % password,
            "chmod 600 ~/.vnc/passwd",
        ]
        _, _, _, stderr = self.exec_command_blocking(';'.join(reset_cmd_lst))
        for line in stderr:
            if "Disk quota exceeded" in line:
                return False, 'Disk quota exceeded'

        return True, ''

    def launch_vnc(self):
        ports_by_me = []
        _, _, stdout, _ = self.exec_command_blocking('vncserver -list')
        for line in stdout:
            this_port_by_me = re.findall(r'\d+', line)
            if len(this_port_by_me) != 0:
                ports_by_me.append(this_port_by_me[0])

        # FIXME: handle disk quota issue when launching vncserver
        relaunch = False
        if len(ports_by_me) > 1:
            # TODO: might recover the valid ones
            # more than one VNC servers are listening and therefore all killed above to prevent unexpected results
            _, _, stdout, _ = self.exec_command_blocking('vncserver -kill ":*"; vncserver')
            relaunch = True
        elif len(ports_by_me) == 0:
            # no valid VNC server is listening
            _, _, stdout, _ = self.exec_command_blocking('vncserver')
            relaunch = True

        vnc_port = None
        if not relaunch:
            vnc_port = int(ports_by_me[0])
        else:
            for vnc_prompt in stdout:
                match = re.search("at :(\d+)", vnc_prompt)
                if match:
                    vnc_port = int(match.group(1))
                    break

        return vnc_port

    def launch_web_vnc(self):
        my_port = self.launch_vnc()

        remote_port = 5900 + my_port
        local_vnc_port = find_free_port()
        local_websocket_port = find_free_port()

        self.port_forward(local_vnc_port, remote_port)

        proxy_thread = threading.Thread(target=websocket_proxy_thread,
                                        args=[local_websocket_port, local_vnc_port])
        proxy_thread.start()

        return local_websocket_port
