#  Copyright (c) 2021-2022 iCtrl Developers
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

import os
import re
import threading

import websockify

from .Connection import Connection
from .vncpasswd import decrypt_passwd, obfuscate_password
from ..utils import find_free_port


def websocket_proxy_thread(local_websocket_port, local_vnc_port):
    if os.environ.get('SSL_CERT_PATH') is None:
        # no certificate provided, run in non-encrypted mode
        # FIXME: consider using a self-signing certificate for local connections
        proxy_server = websockify.LibProxyServer(listen_port=local_websocket_port, target_host='',
                                                 target_port=local_vnc_port,
                                                 run_once=True)
        proxy_server.serve_forever()
        proxy_server.server_close()
    else:
        import subprocess

        subprocess.run(["/var/www/ictrl/application/websockify-other/c/websockify",
                        f'{local_websocket_port}', f':{local_vnc_port}',
                        '--run-once', '--ssl-only',
                        '--cert', os.environ.get('SSL_CERT_PATH'),
                        '--key', os.environ.get('SSL_KEY_PATH')])


class VNC(Connection):
    def __init__(self):
        self.id = None

        super().__init__()

    def __del__(self):
        super().__del__()

    def connect(self, *args, **kwargs):
        return super().connect(*args, **kwargs)

    def get_vnc_password(self):
        _, _, stdout, _ = self.exec_command_blocking('xxd -p ~/.vnc/passwd')
        hexdump = stdout.readline()
        if hexdump == '':
            return False, ''
        else:
            return True, decrypt_passwd(bytearray.fromhex(hexdump))

    def check_5900_open(self):
        _, _, stdout, _ = self.exec_command_blocking('ss -tulpn | grep LISTEN | grep :5900')
        result = stdout.readline()

        if result == '':
            # possibly using mac
            _, _, stdout, _ = self.exec_command_blocking('netstat -an | grep LISTEN | grep .5900')
            result = stdout.readline()

        return result != ''

    def remove_vnc_settings(self):
        remove_cmd_lst = [
            "killall -q -w xvfb-run Xtigervnc",
            "rm -rf ~/.vnc"
        ]
        _, _, _, stderr = self.exec_command_blocking(';'.join(remove_cmd_lst))
        stderr_text = "\n".join(stderr)
        if len(stderr_text):
            return False, stderr_text

        return True, ''

    def reset_vnc_password(self, password):
        hexed_passwd = obfuscate_password(password).hex()

        reset_cmd_lst = [
            # killall -q: don't complain if no process found
            #         -w: wait until the processes to die then continue to the next cmd
            # cp /etc/vnc/xstartup ~/.vnc
            #  : provide a xstartup file to prevent the VNC settings dialog from popping up
            "killall -q -w xvfb-run Xtigervnc",
            "rm -rf ~/.vnc",
            "mkdir ~/.vnc",
            f"printf '{VNC.read_xstartup()}' > ~/.vnc/xstartup",
            "cp /etc/vnc/xstartup ~/.vnc  >& /dev/null",
            "echo '%s'| xxd -r -p > ~/.vnc/passwd" % hexed_passwd,
            "chmod 600 ~/.vnc/passwd",
        ]
        print(f"printf '{VNC.read_xstartup()}' > ~/.vnc/xstartup")
        _, _, _, stderr = self.exec_command_blocking(';'.join(reset_cmd_lst))
        for line in stderr:
            if "Disk quota exceeded" in line:
                return False, 'Disk quota exceeded'

        return True, ''

    def launch_vnc(self):
        ports_by_me = []
        _, _, stdout, _ = self.exec_command_blocking('vncserver -list')
        for line in stdout:
            if 'stale' not in line:
                # if the server was improperly terminated, the status is 'stale'
                this_port_by_me = re.findall(r'\d+', line)
                if len(this_port_by_me) != 0:
                    ports_by_me.append(this_port_by_me[0])

        # FIXME: handle disk quota issue when launching vncserver
        relaunch = False
        relaunch_cmd_list = [
            'vncserver -kill ":*"',
            'killall -q -w xvfb-run Xtigervnc',
            'vncserver'
        ]
        if len(ports_by_me) > 1 or len(ports_by_me) == 0:
            # TODO: might recover the valid ones
            # more than one VNC servers are listening and therefore all killed above to prevent unexpected results
            _, _, stdout, stderr = self.exec_command_blocking(';'.join(relaunch_cmd_list))
            stderr_lines = "".join(stderr.readlines())
            if len(stderr_lines) != 0:
                if 'quota' in stderr_lines:
                    return False, 'QUOTA'
                else:
                    # TODO: can there be any other harmful errors?
                    pass
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

        return True, 5900 + vnc_port

    def create_tunnel(self, remote_port):
        local_vnc_port = find_free_port()
        local_websocket_port = find_free_port()

        self.port_forward(local_vnc_port, remote_port)

        proxy_thread = threading.Thread(target=websocket_proxy_thread,
                                        args=[local_websocket_port, local_vnc_port])
        proxy_thread.start()

        return local_websocket_port

    @staticmethod
    def read_xstartup():
        """
        TODO: read from an actual file instead
        1. Launch a gnome-session so that the VNC config window doesn't show up
        2. To address the bug described at https://bugzilla.redhat.com/show_bug.cgi?id=1710949
           xterm: write to /var/run/utmp
            so that uptime & ruptime can get the correct login count
           xvfb-run: run in the background / don't show GUI
        """
        return "#\\!/bin/sh\\n" \
               "gnome-session &\\n" \
               "timeout 2d xvfb-run -a xterm &\\n"
