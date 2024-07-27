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
import threading
import uuid
from typing import Optional

from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket
from paramiko import Channel
from werkzeug.serving import generate_adhoc_ssl_context

from .Connection import Connection
from .. import app
from ..utils import find_free_port, local_auth, get_headers_dict_from_str
import logging.config

logger = logging.getLogger(__name__)
TERM_CONNECTIONS = {}


class Term(Connection):
    def __init__(self):
        self.id = None
        self.channel: Optional[Channel] = None

        super().__init__()

    def __del__(self):
        print('Terminal::__del__')
        if self.channel:
            self.channel.close()

        super().__del__()

    def connect(self, *args, **kwargs):
        logger.debug("Term: Establishing Term connection")
        return super().connect(*args, **kwargs)

    def launch_shell(self):
        try:
            logger.debug("Term: Launching Shell Terminal")
            self.channel = self.client.invoke_shell('xterm-256color')
        except Exception as e:
            logger.warning(f"Term: Launching Shell Terminal failed with error {str(e)}")
            return False, str(e)

        self.id = uuid.uuid4().hex
        TERM_CONNECTIONS[self.id] = self

        return True, self.id

    def resize(self, width, height):
        try:
            logger.debug(f"Term: Resizing Term to {width}x{height}")
            self.channel.resize_pty(width, height)
        except Exception as e:
            logger.warning(f"Term: Resize Terminal failed with error {str(e)}")
            return False, str(e)

        return True, ''


class TermWebSocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.term = None

    def handleMessage(self):
        logger.debug(f"TermWebSocket: Send message {self.data}")
        self.term.channel.send(self.data)

    def handleConnected(self):
        headers = self.headerbuffer.decode('utf-8')
        headers = get_headers_dict_from_str(headers)
        if not local_auth(headers=headers, abort_func=self.close):
            # local auth failure
            logger.warning("TermWebSocket: Local Authentication Failure")
            return

        logger.debug(f"TermWebSocket: connected to {self.address}")
        print(self.address, 'connected')
        terminal_id = self.request.path[1:]
        if terminal_id not in TERM_CONNECTIONS:
            # print(f'TermWebSocket: Requested terminal_id={terminal_id} does not exist.')
            logger.warning(f"TermWebSocket: Requested terminal_id={terminal_id} does not exist.")
            self.close()
            return

        self.term = TERM_CONNECTIONS[terminal_id]

        def writeall():
            logger.debug("TermWebSocket: Writeall thread started")
            while True:
                data = self.term.channel.recv(1024)
                if not data:
                    # print(f"\r\n*** {terminal_id}: Shell EOF ***\r\n\r\n")
                    logger.debug(f"TermWebSocket: \r\n*** {terminal_id}: Shell EOF ***\r\n\r\n")
                    self.close()
                    break
                self.sendMessage(data)
            logger.debug("TermWebSocket: Writeall thread ended")

        writer = threading.Thread(target=writeall)
        writer.start()

    def handleClose(self):
        logger.debug(f"TermWebSocket: Closing terminal {self.term.id} connection")
        del TERM_CONNECTIONS[self.term.id]
        del self.term


# if the Flask 'app' is in debug mode, all code will be re-run (which means they will run twice) after app.run()
# since the ws server will bind to the port, we should only run it once
# if we are in debug mode, run the server in the second round
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    TERMINAL_PORT = find_free_port()
    print("TERMINAL_PORT =", TERMINAL_PORT)
    logger.debug("Term: Terminal port {}".format(TERMINAL_PORT))

    if os.environ.get('SSL_CERT_PATH') is None:
        logger.debug("Term: SSL Certification Path not set. Generating self-signing certificate")
        # no certificate provided, generate self-signing certificate
        terminal_server = SimpleSSLWebSocketServer('127.0.0.1', TERMINAL_PORT, TermWebSocket,
                                                   ssl_context=generate_adhoc_ssl_context())
    else:
        logger.debug("Term: SSL Certification Path exists")
        import ssl

        terminal_server = SimpleSSLWebSocketServer('0.0.0.0', TERMINAL_PORT, TermWebSocket,
                                                   certfile=os.environ.get('SSL_CERT_PATH'),
                                                   keyfile=os.environ.get('SSL_KEY_PATH'),
                                                   version=ssl.PROTOCOL_TLS)

    threading.Thread(target=terminal_server.serveforever, daemon=True).start()
