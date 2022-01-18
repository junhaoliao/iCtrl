import select
import socketserver
import threading
import typing
from io import StringIO

import paramiko


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.server: ForwardServer
        try:
            chan = self.server.ssh_transport.open_channel(
                "direct-tcpip",
                ("127.0.0.1", self.server.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            return False, "Incoming request to %s:%d failed: %s" % (
                "127.0.0.1", self.server.chain_port, repr(e))

        print(
            "Connected!  Tunnel open %r -> %r -> %r"
            % (
                self.request.getpeername(),
                chan.getpeername(),
                ("127.0.0.1", self.server.chain_port),
            )
        )

        try:
            while True:
                r, _, _ = select.select([self.request, chan], [], [])
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
        except Exception as e:
            print(e)

        try:
            chan.close()
            self.server.shutdown()
        except Exception as e:
            print(e)


class ForwardServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    ssh_transport: paramiko.transport
    chain_port: int


class Connection:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = ""

        self._jump_client: typing.Optional[paramiko.SSHClient] = None
        self._jump_channel: typing.Optional[paramiko.Channel] = None

    def __del__(self):
        self.client.close()
        del self.client

        if self._jump_client is not None:
            self._jump_channel.close()
            self._jump_client.close()
            del self._jump_client

    def _client_connect(self, client: paramiko.SSHClient,
                        host, username,
                        password=None, key_filename=None, private_key_str=None):
        if password is not None:
            client.connect(host, username=username, password=password, timeout=15, sock=self._jump_channel)
        elif key_filename is not None:
            client.connect(host, username=username, key_filename=key_filename, timeout=15, sock=self._jump_channel)
        elif private_key_str is not None:
            pkey = paramiko.RSAKey.from_private_key(StringIO(private_key_str))
            client.connect(host, username=username, pkey=pkey, timeout=15, sock=self._jump_channel)
        else:
            raise ValueError("Connection: no valid SSH auth given.")

    def _init_jump_channel(self, host, username, **auth_methods):
        """
        init jump client channel only if the target is an ECF machine which normally requires a VPN connection
        The remote.ecf.utoronto.ca host doesn't require VPN to access and therefore can be used as a jump server

        :param host:
        :param username:
        :param auth_methods:
        :return:
        """
        if (host.endswith('ecf.utoronto.ca') or host.endswith('ecf.toronto.edu')) and not host.startswith('remote'):
            if self._jump_client is not None:
                raise ValueError("API misuse: should not invoke connect twice on the same Connection object")

            self._jump_client = paramiko.SSHClient()
            self._jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._client_connect(self._jump_client, 'remote.ecf.utoronto.ca', username, **auth_methods)
            self._jump_channel = self._jump_client.get_transport().open_channel('direct-tcpip',
                                                                                (host, 22),
                                                                                ('0.0.0.0', 22))

    def connect(self, host: str, username: str, **auth_methods):
        try:
            self._init_jump_channel(host, username, **auth_methods)
            self._client_connect(self.client, host, username, **auth_methods)
        except Exception as e:
            # raise e
            # print('Connection::connect() exception:')
            return False, str(e)

        self.host = host

        return True, ''

    @staticmethod
    def ssh_keygen(key_filename=None, key_file_obj=None, public_key_comment=''):
        """ Generate and save an RSA SSH private key on the local machine, return a public key
        :param key_filename: path to which the private key should be saved
        :param key_file_obj: file object in which the private key should be saved
        :param public_key_comment: comment to be added at the end of the public key record
        :return: passphrase of the public key
        """
        # 3072 is the default size of OpenSSH keys
        rsa_key = paramiko.RSAKey.generate(3072)

        # save the private key
        if key_filename is not None:
            rsa_key.write_private_key_file(key_filename)
        elif key_file_obj is not None:
            rsa_key.write_private_key(key_file_obj)
        else:
            raise ValueError('Neither key_filename nor key_file_obj is provided.')

        # ssh-rsa: key type
        # rsa_key.get_base64(): key phrase
        return "ssh-rsa " + rsa_key.get_base64() + " " + public_key_comment

    def save_keys(self, key_filename=None, key_file_obj=None, public_key_comment=''):
        """ Generate an RSA SSH key. Save the private key on the local machine, and save the public one on the remote.
        Must be called only when the client is connected.
        :param key_filename: path to which the private key should be saved
        :param key_file_obj: file object in which the private key should be saved
        :param public_key_comment: comment to be added at the end of the public key record
        :return: None
        """
        if key_filename is not None:
            # generate key pairs and save the private key on the local machine
            pub_key = Connection.ssh_keygen(key_filename=key_filename, public_key_comment=public_key_comment)
        elif key_file_obj is not None:
            # generate key pairs and save the private key in the key file object
            pub_key = Connection.ssh_keygen(key_file_obj=key_file_obj, public_key_comment=public_key_comment)
        else:
            raise ValueError('Neither key_filename nor key_file_obj is provided.')

        # save the public key onto the remote server
        exit_status, _, _, _ = self.exec_command_blocking(
            "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '%s' >>  ~/.ssh/authorized_keys" % pub_key)
        if exit_status != 0:
            return False, "Connection::save_keys: unable to save public key"

        return True, ""

    def exec_command_blocking(self, command):
        """ Execute some command on the remote and return the exit_status and the outputs of the execution.
        NOTE: This function is blocking.
        :param command: command to be executed
        :return: exit_status, stdin, stdout, stderr of the executed command
        """
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()

        return exit_status, stdin, stdout, stderr

    def _port_forward_thread(self, local_port, remote_port):
        forward_server = ForwardServer(("", local_port), Handler)

        forward_server.ssh_transport = self.client.get_transport()
        forward_server.chain_port = remote_port

        forward_server.serve_forever()
        forward_server.server_close()

    def port_forward(self, *args):
        forwarding_thread = threading.Thread(target=self._port_forward_thread, args=args)
        forwarding_thread.start()

    def is_eecg(self):
        return 'eecg' in self.host

    def is_ecf(self):
        return 'ecf' in self.host

    def is_uoft(self):
        return self.is_eecg() or self.is_ecf()
