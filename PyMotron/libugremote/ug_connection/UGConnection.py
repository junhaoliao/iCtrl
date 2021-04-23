import base64
import json
import threading

import paramiko
import zmq


class UGConnection:
    # TODO: check variable namings and hide the attributes that should be private
    """ SSH connection for communication between the client and the remote server
    >>> # DONE_TODO: remove credentials before commit
    >>> HOSTNAME = "ug250.eecg.toronto.edu"
    >>> USERNAME = "liaojunh"
    >>> PASSWD = "5t6y7u8i"
    >>> KEY_FILENAME = "./profile/id_rsa"
    >>> # supply only passwd
    >>> conn = UGConnection()
    >>> conn.connect(HOSTNAME, USERNAME, passwd=PASSWD)
    >>> _, stdout, _ = conn.exec_command("ls")
    >>> for line in stdout:
    ...     print(line) # doctest: +ELLIPSIS
    total...
    >>> # reuse conn
    >>> conn.connect(HOSTNAME, USERNAME, passwd=PASSWD) # doctest: +ELLIPSIS
    Connection already established on ...
    >>> # save keys
    >>> import os
    >>> from os import path
    >>> if path.isfile(KEY_FILENAME):
    ...     os.remove(KEY_FILENAME)
    >>> conn.save_keys(KEY_FILENAME)
    >>> path.isfile(KEY_FILENAME)
    True
    >>> # disconnect conn
    >>> conn.disconnect()
    >>> # supply invalid credentials
    >>> try:
    ...     conn.connect(HOSTNAME, USERNAME, passwd="1234")
    ... except paramiko.ssh_exception.AuthenticationException as e:
    ...     print(e)
    Authentication failed.
    >>> # supply invalid hostname
    >>> import socket
    >>> try:
    ...     conn.connect("invalid_host", USERNAME, PASSWD)
    ... except socket.gaierror as e:
    ...     print(e)
    [Errno 8] nodename nor servname provided, or not known
    >>> # supply key_filename
    >>> conn.connect(HOSTNAME, USERNAME, key_filename=KEY_FILENAME)
    >>> _, stdout, _ = conn.exec_command("ls")
    >>> for line in stdout: # doctest: +ELLIPSIS
    ...     print(line)
    total...
    >>> # TODO: add shell test cases: can do it at higher levels
    >>> conn.open_sftp()
    >>> conn.sftp_ls("") # doctest:+ELLIPSIS
    ('...', [...])
    >>> conn.sftp_ls("Downloads") # doctest:+ELLIPSIS
    ('...', [...])
    >>> conn.sftp_ls("..")  # doctest:+ELLIPSIS
    ('...', [...])
    >>> conn.sftp_ls("/") # doctest:+ELLIPSIS
    ('...', [...])
    >>> conn.close_sftp()
    """

    def __init__(self):
        self.connected = False

        self.hostname = None
        self.username = None

        self.client = paramiko.SSHClient()
        # TODO: should prompt the user to confirm the host key if missing
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.shell_chan = None

        self.sftp = None

    def connect(self, hostname, username, passwd=None, key_filename=None):
        """ Connect to the remote server

        :param hostname: remote server host name
        :param username: user name on the remote server
        :param passwd: password for user authentication
        :param key_filename: (unused if passwd is not None) private RSA key for user authentication
        :return: None
        """
        # if the client is already connected, we should attempt to reuse the connection
        if self.connected:
            if hostname == self.hostname and username == self.username:
                # the hostname and username match what we have right now
                # reuse the connection
                print("Connection already established on %s@%s" % (username, hostname))
                return
            else:
                # the hostname and username don't match what we have right now
                print("Hostname or credential mismatch. Disconnect that connection. ")

        # if the client is not connected or can't be reused
        self.disconnect()
        try:
            # assume connect() is called correctly (only passwd or key_filename is supplied):
            #   1) if passwd is not None, use password to login
            #   2) if passwd is None and key_filename is not None, use key to login
            #   3) if passwd is None and key_filename is None, raise an invalid-argument exception
            if passwd is not None:
                # try connecting to the host
                self.client.connect(hostname,
                                    username=username,
                                    password=passwd)
            elif key_filename is not None:
                self.client.connect(hostname,
                                    username=username,
                                    key_filename=key_filename)
            else:
                raise ValueError("Invalid arguments: Both passwd and key_filename are None. ")
            # save the hostname and username
            #  for checking whether the connection can be reused
            self.hostname = hostname
            self.username = username
            self.connected = True
        except Exception as e:
            # common exceptions include
            #   1) Authentication Error
            #       paramiko.ssh_exception.AuthenticationException: Authentication failed.
            #   2) Hostname Error
            #       socket.gaierror: [Errno 8] nodename nor servname provided, or not known
            raise e

    def disconnect(self):
        """ Disconnect the SSH client "client"

        :return: None
        """
        self.disconnect_shell()
        self.close_sftp()
        self.client.close()

        self.hostname = None
        self.username = None
        self.connected = False

    @staticmethod
    def ssh_keygen(key_filename):
        """ Generate and save an RSA SSH private key on the local machine, return a public key

        :param key_filename: path to where the private key should be saved
        :return: passphrase of the public key
        """
        # 2048 is the default size of RSA keys
        rsa_key = paramiko.RSAKey.generate(2048)

        # save the private key
        rsa_key.write_private_key_file(key_filename)

        # get the username and hostname for saving those on the remote server
        import getpass
        import socket
        os_username = getpass.getuser()
        os_hostname = socket.gethostname()

        # ssh-rsa: key type
        # rsa_key.get_base64(): key phrase
        # os_username + "@" + os_hostname: for identification on the remote server
        return "ssh-rsa " + rsa_key.get_base64() + " " + os_username + "@" + os_hostname

    def save_keys(self, key_filename):
        """ Generate an RSA SSH key. Save the private key on the local machine, and save the public one on the remote.

        :param key_filename: path to where the private key should be saved
        :return: None
        """
        if not self.connected:
            raise PermissionError("Misuse: Client not connected.")

        # generate and save the private key on the local machine
        pub_key = UGConnection.ssh_keygen(key_filename)
        # save the public key onto the remote server
        exit_status, _, _, _ = self.exec_command_blocking(
            "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '%s' >>  ~/.ssh/authorized_keys" % pub_key)
        if exit_status != 0:
            raise SystemError("Not able to save pub key on the remote, exit_status=%d" % exit_status)

    def exec_command(self, command):
        """ Execute some command on the remote and return the outputs.
        NOTE: This function is non-blocking. If blocking is required, call recv_exit_status() on the channel. e.g.
            stdout.channel.recv_exit_status()

        :param command: command to be executed
        :return: stdin, stdout, stderr of the executed command
        """
        return self.client.exec_command(command)

    def exec_command_blocking(self, command):
        """ Execute some command on the remote and return the exit_status and the outputs of the execution.
        NOTE: This function is blocking.

        :param command: command to be executed
        :return: exit_status, stdin, stdout, stderr of the executed command
        """
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()

        return exit_status, stdin, stdout, stderr

    def invoke_shell(self, session, ipc_send):
        if self.shell_chan is not None:
            raise RuntimeError("UGConnection: invoke_shell: shell already invoked.")
        self.shell_chan = self.client.invoke_shell()

        def writeall():
            while True:
                data = self.shell_chan.recv(1024)
                if not data:
                    print("\r\n*** EOF ***\r\n\r\n")
                    break
                msg = {
                    "recv": {
                        "s": session,
                        "d": base64.b64encode(data).decode("utf-8")
                    }
                }
                ipc_send.send_string(json.dumps(msg))

        writer = threading.Thread(target=writeall)
        writer.start()

    def shell_send_data(self, data):
        if self.shell_chan is None:
            raise RuntimeError("UGConnection: shell_send_data: shell used before invoke.")
        self.shell_chan.send(data)

    def shell_change_size(self, width, height):
        if self.shell_chan is None:
            raise RuntimeError("UGConnection: shell_send_data: shell used before invoke.")
        self.shell_chan.resize_pty(width, height)

    def disconnect_shell(self):
        if self.shell_chan is not None:
            self.shell_chan.close()
        self.shell_chan = None

    def open_sftp(self):
        # should only be called if the sftp handle isn't setup (self.sftp is None)
        t = self.client.get_transport()
        self.sftp = paramiko.SFTPClient.from_transport(t)
        self.sftp.chdir(".")

    def sftp_ls(self, path):
        if self.sftp is None:
            self.open_sftp()

        if path != "":
            self.sftp.chdir(path)
        cwd = self.sftp.getcwd()
        attrs = self.sftp.listdir_attr(cwd)

        file_list = []
        # TODO: should support uid and gid later
        for file_attr in attrs:
            file = {
                "name": file_attr.filename,
                "mode": file_attr.st_mode,
                "size": file_attr.st_size,
                "atime": file_attr.st_atime,
                "mtime": file_attr.st_mtime
            }
            file_list.append(file)

        return cwd, file_list

    def close_sftp(self):
        if self.sftp is not None:
            self.sftp.close()

    def create_forward_tunnel(self, local_port, remote_port):
        import socketserver

        class Handler(socketserver.BaseRequestHandler):
            # TODO: revisit the need to override setup() and finish() instead of
            #  putting everything in handle()
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

                import select
                try:
                    while True:
                        r, _, _ = select.select([handler_self.request, chan], [], [])
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
                    return

                try:
                    peername = handler_self.request.getpeername()
                    chan.close()
                    handler_self.request.close()
                    print("Tunnel closed from %r" % (peername,))
                except Exception as e:
                    print(e)

                handler_self.server.shutdown()
                handler_self.server.server_close()
                print("successfully disconnected")

        class ForwardServer(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True

        forward_srv = ForwardServer(("", local_port), Handler)

        forward_thread = threading.Thread(target=forward_srv.serve_forever)
        forward_thread.start()
