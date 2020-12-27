import select
import socketserver
import threading

import paramiko

import exceptions


class UGConnection():
    def __init__(self):
        self.connected = False

        self.hostname = None
        self.username = None
        self.passwd = None

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())

        self.forward_thread = None

    def connect(self, hostname, username, passwd):
        if self.connected:
            print("Connection already established on %s@%s" % (username, hostname))
            if self.hostname == hostname and self.username == username and self.passwd == passwd:
                print("Found same credentials on same host. Keep using that connection. ")
                return
            else:
                print("Hostname or credential mismatch. Disconnect that connection. ")
                self.disconnect()

        # anyone who calls UGConnection.connect() should handle exceptions
        #  i.e. use UGConnection.connect() in a try-block
        self.client.connect(hostname, username=username, password=passwd)

        self.hostname = hostname
        self.username = username
        self.passwd = passwd

        self.connected = True

    def disconnect(self):
        self.client.close()

        self.hostname = None
        self.username = None
        self.passwd = None

        self.connected = False

    def create_forward_tunnel(self, local_port, remote_port):
        class Handler(socketserver.BaseRequestHandler):
            chain_host = "localhost"
            chain_port = remote_port
            ssh_transport = self.client.get_transport()

            def handle(handler_self):
                try:
                    chan = handler_self.ssh_transport.open_channel(
                        "direct-tcpip",
                        (handler_self.chain_host, handler_self.chain_port),
                        handler_self.request.getpeername(),
                    )
                except Exception as e:
                    raise exceptions.NetworkError(
                        "Incoming request to %s:%d failed: %s"
                        % (handler_self.chain_host, handler_self.chain_port, repr(e))
                    )
                if chan is None:
                    raise exceptions.NetworkError(
                        "Incoming request to %s:%d was rejected by the SSH server."
                        % (handler_self.chain_host, handler_self.chain_port)
                    )

                print(
                    "Connected!  Tunnel open %r -> %r -> %r"
                    % (
                        handler_self.request.getpeername(),
                        chan.getpeername(),
                        (handler_self.chain_host, handler_self.chain_port),
                    )
                )

                try:
                    while True:
                        r, w, x = select.select([handler_self.request, chan], [], [])
                        if handler_self.request in r:
                            data = handler_self.request.recv(1024)
                            if len(data) == 0:
                                break
                            chan.send(data)
                        if chan in r:
                            data = chan.recv(1024)
                            if len(data) == 0:
                                break
                            handler_self.request.send(data)
                except (ConnectionResetError, BrokenPipeError):
                    print("Likely TigerVNC Viewer has been closed, or the network is interrupted, "
                          "shutting down")

                try:
                    # race might happen when getting peername; use try-block instead
                    peername = handler_self.request.getpeername()
                    chan.close()
                    handler_self.request.close()
                    print("Tunnel closed from %r" % (peername,))
                except Exception as e:
                    print(e)

                handler_self.server.shutdown()
                handler_self.server.server_close()
                self.disconnect()
                print("successfully disconnected")

        class ForwardServer(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True

        # put in a while-loop to deal with any "OSError: [Errno 48] Address already in use" exception,
        #  when someone is playing around with the script by keeping terminating and
        #  opening the connections too soon...
        # while True:
        #     try:
        forward_srv = ForwardServer(("", local_port), Handler)
        # except OSError:
        #     continue
        # break

        self.forward_thread = threading.Thread(target=forward_srv.serve_forever)
        self.forward_thread.start()
