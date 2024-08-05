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

import logging
import os
import re
import threading

from .Connection import Connection
from .mywebsockify import MyProxyRequestHandler, MySSLProxyServer
from .vncpasswd import decrypt_passwd
from ..utils import find_free_port
import logging.config

logger = logging.getLogger(__name__)

def websocket_proxy_thread(local_websocket_port, local_vnc_port):
    logger.debug("VNC: Start websocket proxy thread")
    if os.environ.get('SSL_CERT_PATH') is None:
        logger.debug("VNC: SSL Certification Path not set. Initialize SSL Proxy Server.")
        proxy_server = MySSLProxyServer(RequestHandlerClass=MyProxyRequestHandler,
                                        listen_port=local_websocket_port, target_host='',
                                        target_port=local_vnc_port)

        # only serve two request:
        #  1st: first handshake: upgrade the HTTP request
        #  2nd: actually serve the ws connection
        for _ in range(2):
            if _ == 0:
                logger.debug("VNC: Handle HTTP request")
            else:
                logger.debug("VNC: Handle WebSocket connection")
            proxy_server.handle_request()
        logger.debug("VNC: Close SSL Proxy Server")
        proxy_server.server_close()
    else:
        logger.debug("VNC: SSL Certification Path exists")
        import subprocess

        logger.debug(f"VNC: Run websockify on websocket port {local_websocket_port} and vncport {local_vnc_port}")
        subprocess.run(["/var/www/ictrl/application/websockify-other/c/websockify",
                        f'{local_websocket_port}', f':{local_vnc_port}',
                        '--run-once', '--ssl-only',
                        '--cert', os.environ.get('SSL_CERT_PATH'),
                        '--key', os.environ.get('SSL_KEY_PATH')])
    logger.debug("VNC: End websocket proxy thread")


class VNC(Connection):
    def __init__(self):
        self.id = None

        super().__init__()

    def __del__(self):
        print('VNC::__del__')
        super().__del__()

    def connect(self, *args, **kwargs):
        logger.debug("VNC: Establishing VNC connection")
        return super().connect(*args, **kwargs)

    def get_vnc_password(self):
        _, _, stdout, _ = self.exec_command_blocking("hexdump --format '16/1 \"%02x\"' ~/.vnc/passwd")
        hexdump = stdout.readline().rstrip()
        if hexdump == '':
            logger.warning("VNC: VNC Password is empty")
            return False, ''
        else:
            return True, decrypt_passwd(bytearray.fromhex(hexdump))

    def check_5900_open(self):
        _, _, stdout, _ = self.exec_command_blocking('ss -tulpn | grep LISTEN | grep ":5900 "')
        result = stdout.readline()

        if result == '':
            # possibly using mac
            _, _, stdout, _ = self.exec_command_blocking('netstat -an | grep LISTEN | grep "\.5900 "')
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
            logger.warning(f"VNC: Error removing VNC settings: {stderr_text}")
            return False, stderr_text

        return True, ''

    def reset_vnc_password(self, password):
        reset_cmd_lst = [
            # killall -q: don't complain if no process found
            #         -w: wait until the processes to die then continue to the next cmd
            # cp /etc/vnc/xstartup ~/.vnc
            #  : provide a xstartup file to prevent the VNC settings dialog from popping up
            "killall -q -w xvfb-run Xtigervnc",

            "rm -rf ~/.vnc",
            "mkdir ~/.vnc",

            # FIXME: re-enable xstartup config
            # f"printf '{XSTARTUP_STR}' > ~/.vnc/xstartup",
            # "cp /etc/vnc/xstartup ~/.vnc  >& /dev/null",
            # "chmod 700 ~/.vnc/xstartup",

            "echo '%s'| vncpasswd -f > ~/.vnc/passwd" % password,
            "chmod 600 ~/.vnc/passwd",
        ]
        _, _, _, stderr = self.exec_command_blocking(';'.join(reset_cmd_lst))
        error_lines = []
        for line in stderr:
            logger.warning("VNC: Error resetting VNC password: %s", line)

            if "Disk quota exceeded" in line:
                return False, 'Disk quota exceeded'
            else:
                error_lines.append(line)
        if len(error_lines) != 0:
            return False, "".join(error_lines)

        return True, ''

    def launch_vnc(self):
        ports_by_me = []
        _, _, stdout, _ = self.exec_command_blocking('vncserver -list')
        logger.debug("VNC: Listing vnc servers")
        for line in stdout:
            if 'stale' not in line:
                # if the server was improperly terminated, the status is 'stale'
                this_port_by_me = re.findall(r'\d+', line)
                if len(this_port_by_me) != 0:
                    ports_by_me.append(this_port_by_me[0])
            if line.strip() != "":
                logger.debug("VNC: VNC server list output: %s", line.strip())

        # FIXME: handle disk quota issue when launching vncserver
        relaunch = False
        relaunch_cmd_list = [
            'vncserver -kill ":*"',
            'killall -q -w xvfb-run Xtigervnc',
            'vncserver'
        ]
        if len(ports_by_me) > 1 or len(ports_by_me) == 0:
            logger.debug("VNC: Relaunch VNC servers")
            # TODO: might recover the valid ones
            # more than one VNC servers are listening and therefore all killed above to prevent unexpected results
            _, _, stdout, stderr = self.exec_command_blocking(';'.join(relaunch_cmd_list))
            stderr_lines = "".join(stderr.readlines())
            if len(stderr_lines) != 0:
                logger.warning("VNC: Error relaunching VNC servers: %s", stderr_lines)
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
                match = re.search(":(\d+)", vnc_prompt)
                if match:
                    vnc_port = int(match.group(1))
                    break
        logger.debug("VNC: VNC port: %s", vnc_port)

        # FIXME: use a better condition than is_eecg
        """
        To address a bug described at https://bugzilla.redhat.com/show_bug.cgi?id=1710949
           xterm: write to /var/run/utmp so that uptime & ruptime can get the correct login count
           xvfb-run: run in the background / don't show GUI
        """
        if self.is_eecg():
            self.exec_command_blocking("pgrep -cxu $USER Xvfb || ( timeout 12h xvfb-run -a xterm & )")

        return True, 5900 + vnc_port

    def create_tunnel(self, remote_port):
        local_vnc_port = find_free_port()
        local_websocket_port = find_free_port()
        logger.debug(f"VNC: Local VNC Port is {local_vnc_port}")
        logger.debug(f"VNC: Local Web Socket Port is {local_websocket_port}")
        self.port_forward(local_vnc_port, remote_port)

        proxy_thread = threading.Thread(target=websocket_proxy_thread,
                                        args=[local_websocket_port, local_vnc_port])
        proxy_thread.start()

        return local_websocket_port
