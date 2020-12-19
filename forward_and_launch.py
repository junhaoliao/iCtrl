import os
import select
import socketserver as SocketServer
import sys
import threading

import paramiko

from path_names import *

g_verbose = True
fsrv = None


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.chain_host, self.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            verbose(
                "Incoming request to %s:%d failed: %s"
                % (self.chain_host, self.chain_port, repr(e))
            )
            return
        if chan is None:
            verbose(
                "Incoming request to %s:%d was rejected by the SSH server."
                % (self.chain_host, self.chain_port)
            )
            return

        verbose(
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
            verbose("likely TigerVNC viewer has been closed, or the network is interrupted, "
                    "shutting down")
        else:
            peername = self.request.getpeername()
            chan.close()
            self.request.close()
            verbose("Tunnel closed from %r" % (peername,))

        global fsrv
        if fsrv is not None:
            fsrv.shutdown()
            fsrv = None


def forward_tunnel(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHandler(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport

    global fsrv
    print("localport: " + str(local_port))
    fsrv = ForwardServer(("", local_port), SubHandler)
    fsrv.serve_forever()


def verbose(s):
    if g_verbose:
        print(s)


def get_host_port(spec, default_port):
    "parse 'hostname:22' into a host and port, with the port optional"
    args = (spec.split(":", 1) + [default_port])[:2]
    args[1] = int(args[1])
    return args[0], args[1]


forward_thread = None


def forward_and_launch(srv_num, port, username, ug_passwd):
    server = "ug%s.eecg.toronto.edu" % srv_num
    remote_host = "localhost"
    vnc_port = 5900 + port

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    try:
        client.connect(
            server,
            22,
            username=username,
            password=ug_passwd,
        )
    except Exception as e:
        print("*** Failed to connect to %s:%d: %r" % (server, 22, e))
        sys.exit(1)

    _, stdout, stderr = client.exec_command('vncserver :' + str(port))

    for line in stderr:
        print('... ' + line.strip('\n'))

    global forward_thread
    try:
        forward_thread = threading.Thread(target=forward_tunnel,
                                          args=(vnc_port, remote_host, vnc_port, client.get_transport()))
        forward_thread.start()
    except KeyboardInterrupt:
        print("C-c: Port forwarding stopped.")
        os._exit(0)

    if os.name == 'posix': # TODO: no way this is not gonna work on other posix systems
        import subprocess
        subprocess.Popen([VNC_VIEWER_PATH_MACOS, "--passwd=%s" % VNC_PASSWD_PATH, "localhost:%d" % vnc_port])
    else:
        import subprocess
        subprocess.Popen([VNC_VIEWER_PATH_WIN64, "--passwd=%s"%VNC_PASSWD_PATH, "localhost:%d"%vnc_port])

    forward_thread.join()
    os._exit(0)
