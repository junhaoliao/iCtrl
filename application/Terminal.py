import os
import threading
import uuid

from simple_websocket_server import WebSocketServer, WebSocket

from application.Connection import Connection


class Terminal(Connection):
    def __init__(self):
        self.id = None
        self.channel = None

        super().__init__()

    def __del__(self):
        print('Terminal::__del__')
        self.channel.close()
        super().__del__()

    def connect(self, *args, **kwargs):
        super().connect(*args, **kwargs)

        try:
            self.channel = self.client.invoke_shell()
        except Exception as e:
            return False, str(e)

        self.id = uuid.uuid4().hex
        terminal_connections[self.id] = self

        return True, self.id


terminal_connections: dict[str, Terminal] = {}


class TerminalSocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.term = None

    def handle(self):
        self.term.channel.send(self.data)

    def connected(self):
        print(self.address, 'connected')
        terminal_id = self.request.path[1:]
        if terminal_id not in terminal_connections:
            print(f'TerminalSocket: Requested terminal_id={terminal_id} does not exist.')
            self.close()

        self.term = terminal_connections[terminal_id]

        def writeall():
            while True:
                data = self.term.channel.recv(1024)
                if not data:
                    print("\r\n*** Shell EOF ***\r\n\r\n")
                    break
                self.send_message(data)

        writer = threading.Thread(target=writeall)
        writer.start()

    def handle_close(self):
        print(self.address, 'closed')
        del terminal_connections[self.term.id]
        del self.term


if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    terminal_server = WebSocketServer('', 8000, TerminalSocket)
    threading.Thread(target=terminal_server.serve_forever).start()