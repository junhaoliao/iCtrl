import paramiko


class Connection:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __del__(self):
        self.client.close()

    def connect(self, host, username, password=None, key_filename=None):
        try:
            if password is not None:
                self.client.connect(host, username=username, password=password)
            elif key_filename is not None:
                self.client.connect(host, username=username, key_filename=key_filename)
            else:
                # TODO: read the docs and the RFC to check whether this is allowed
                raise ValueError("Connection: no valid SSH auth given.")
        except Exception as e:
            return False, str(e)

        return True, ""

    @staticmethod
    def ssh_keygen(key_filename):
        """ Generate and save an RSA SSH private key on the local machine, return a public key
        :param key_filename: path to where the private key should be saved
        :return: passphrase of the public key
        """
        # 3072 is the default size of OpenSSH keys
        rsa_key = paramiko.RSAKey.generate(3072)

        # save the private key
        rsa_key.write_private_key_file(key_filename)

        # ssh-rsa: key type
        # rsa_key.get_base64(): key phrase
        return "ssh-rsa " + rsa_key.get_base64() + " " + key_filename

    def save_keys(self, key_filename):
        """ Generate an RSA SSH key. Save the private key on the local machine, and save the public one on the remote.
        Must be called only when the client is connected.
        :param key_filename: path to where the private key should be saved
        :return: None
        """
        # generate and save the private key on the local machine
        pub_key = Connection.ssh_keygen(key_filename)
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

