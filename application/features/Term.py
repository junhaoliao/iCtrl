import os
import threading
import uuid
from typing import Optional

from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket, SimpleWebSocketServer
from paramiko import Channel

from .Connection import Connection
from .. import app
from ..utils import find_free_port

terminal_connections = {}


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
        return super().connect(*args, **kwargs)

    def launch_shell(self):
        try:
            self.channel = self.client.invoke_shell('xterm-256color')
        except Exception as e:
            return False, str(e)

        self.id = uuid.uuid4().hex
        terminal_connections[self.id] = self

        return True, self.id

    def resize(self, width, height):
        try:
            self.channel.resize_pty(width, height)
        except Exception as e:
            return False, str(e)

        return True, ''


class TerminalSocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.term = None

    def handleMessage(self):
        self.term.channel.send(self.data)

    def handleConnected(self):
        print(self.address, 'connected')
        terminal_id = self.request.path[1:]
        if terminal_id not in terminal_connections:
            print(f'TerminalSocket: Requested terminal_id={terminal_id} does not exist.')
            self.close()
            return

        self.term = terminal_connections[terminal_id]

        def writeall():
            while True:
                data = self.term.channel.recv(1024)
                if not data:
                    print(f"\r\n*** {terminal_id}: Shell EOF ***\r\n\r\n")
                    self.close()
                    break
                self.sendMessage(data)

        writer = threading.Thread(target=writeall)
        writer.start()

    def handleClose(self):
        print(self.address, 'closed')
        del terminal_connections[self.term.id]
        del self.term


# if the Flask 'app' is in debug mode, all code will be re-run (which means they will run twice) after app.run()
# since the ws server will bind to the port, we should only run it once
# if we are in debug mode, run the server in the second round
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    TERMINAL_PORT = find_free_port()
    if os.environ.get('SSL_CERT_PATH') is None:
        # no certificate provided, run in non-encrypted mode
        # FIXME: consider using a self-signing certificate for local connections
        terminal_server = SimpleWebSocketServer('', TERMINAL_PORT, TerminalSocket)
    else:
        import ssl

        terminal_server = SimpleSSLWebSocketServer('', TERMINAL_PORT, TerminalSocket,
                                                   certfile=os.environ.get('SSL_CERT_PATH'),
                                                   keyfile=os.environ.get('SSL_KEY_PATH'),
                                                   version=ssl.PROTOCOL_TLS)

    threading.Thread(target=terminal_server.serveforever).start()
