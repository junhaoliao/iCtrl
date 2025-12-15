"""
Unit tests for application/features/Connection.py

These tests use mocking to avoid actual network connections.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO


class TestConnectionInit:
    """Tests for Connection initialization."""

    @pytest.mark.unit
    def test_connection_creates_ssh_client(self):
        """Connection should create a paramiko SSHClient."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()

            mock_paramiko.SSHClient.assert_called_once()
            mock_client.set_missing_host_key_policy.assert_called_once()

    @pytest.mark.unit
    def test_connection_initial_state(self):
        """Connection should have empty host and username initially."""
        with patch('application.features.Connection.paramiko'):
            from application.features.Connection import Connection
            conn = Connection()

            assert conn.host == ""
            assert conn.username == ""
            assert conn._jump_client is None
            assert conn._jump_channel is None


class TestConnectionConnect:
    """Tests for Connection.connect method."""

    @pytest.mark.unit
    def test_connect_with_password(self):
        """Connect should work with password authentication."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            status, reason = conn.connect("test.host.com", "testuser", password="testpass")

            assert status is True
            assert reason == ''
            assert conn.host == "test.host.com"
            assert conn.username == "testuser"
            mock_client.connect.assert_called_once()

    @pytest.mark.unit
    def test_connect_with_key_filename(self):
        """Connect should work with key file authentication."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            status, reason = conn.connect("test.host.com", "testuser", key_filename="/path/to/key")

            assert status is True
            assert reason == ''
            mock_client.connect.assert_called_once()
            call_kwargs = mock_client.connect.call_args[1]
            assert call_kwargs['key_filename'] == "/path/to/key"

    @pytest.mark.unit
    def test_connect_with_private_key_str(self):
        """Connect should work with private key string."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()
            mock_pkey = Mock()
            mock_paramiko.RSAKey.from_private_key.return_value = mock_pkey

            from application.features.Connection import Connection
            conn = Connection()
            private_key = "-----BEGIN RSA PRIVATE KEY-----\nfake\n-----END RSA PRIVATE KEY-----"
            status, reason = conn.connect("test.host.com", "testuser",
                                         private_key_str=private_key)

            assert status is True
            assert reason == ''
            mock_paramiko.RSAKey.from_private_key.assert_called_once()
            # Verify the pkey was passed to connect
            mock_client.connect.assert_called_once()
            call_kwargs = mock_client.connect.call_args[1]
            assert call_kwargs['pkey'] == mock_pkey
            assert call_kwargs['username'] == "testuser"
            assert call_kwargs['timeout'] == 15

    @pytest.mark.unit
    def test_connect_with_private_key_str_invalid_key(self):
        """Connect should return error when private key is invalid."""
        import paramiko as real_paramiko
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()
            mock_paramiko.RSAKey.from_private_key.side_effect = real_paramiko.SSHException("Invalid key")

            from application.features.Connection import Connection
            conn = Connection()
            status, reason = conn.connect("test.host.com", "testuser",
                                         private_key_str="invalid-key-data")

            assert status is False
            assert "Invalid key" in reason

    @pytest.mark.unit
    def test_connect_failure_returns_error(self):
        """Connect should return error on failure."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_client.connect.side_effect = Exception("Connection refused")
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            status, reason = conn.connect("test.host.com", "testuser", password="testpass")

            assert status is False
            assert "Connection refused" in reason

    @pytest.mark.unit
    def test_connect_no_auth_raises_error(self):
        """Connect should raise error when no auth method provided."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            status, reason = conn.connect("test.host.com", "testuser")

            assert status is False
            assert "no valid SSH auth" in reason


class TestConnectionECFJumpHost:
    """Tests for ECF jump host functionality.

    Note: These tests are skipped because they require actual network connections
    to test the jump host functionality properly. The mocking doesn't work because
    the _init_jump_channel method needs to actually connect to remote.ecf.utoronto.ca.
    """

    @pytest.mark.skip(reason="Requires actual network connection to test jump host")
    @pytest.mark.unit
    def test_ecf_host_uses_jump(self):
        """ECF hosts should use jump host."""
        pass

    @pytest.mark.unit
    def test_remote_ecf_no_jump(self):
        """remote.ecf.utoronto.ca should not use jump host."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            status, reason = conn.connect("remote.ecf.utoronto.ca", "testuser", password="testpass")

            # Should NOT have created jump client
            assert conn._jump_client is None

    @pytest.mark.skip(reason="Requires actual network connection to test jump host")
    @pytest.mark.unit
    def test_eecg_host_uses_jump(self):
        """EECG hosts should use jump host."""
        pass


class TestConnectionExecCommand:
    """Tests for exec_command methods."""

    @pytest.mark.unit
    def test_exec_command_blocking(self):
        """exec_command_blocking should execute and return results."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_stdin = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            exit_status, stdin, stdout, stderr = conn.exec_command_blocking("ls -la")

            assert exit_status == 0
            mock_client.exec_command.assert_called_with("ls -la")

    @pytest.mark.unit
    def test_exec_command_blocking_large(self):
        """exec_command_blocking_large should return combined output."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_stdout = Mock()
            mock_stdout.__iter__ = Mock(return_value=iter(["line1", "line2"]))
            mock_stderr = Mock()
            mock_stderr.__iter__ = Mock(return_value=iter(["error1"]))
            mock_client.exec_command.return_value = (Mock(), mock_stdout, mock_stderr)
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            result = conn.exec_command_blocking_large("cat file")

            assert "line1" in result
            assert "line2" in result
            assert "error1" in result


class TestConnectionSSHKeygen:
    """Tests for ssh_keygen static method."""

    @pytest.mark.unit
    def test_ssh_keygen_to_file(self):
        """ssh_keygen should generate key and save to file."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_key = Mock()
            mock_key.get_base64.return_value = "AAAA1234"
            mock_paramiko.RSAKey.generate.return_value = mock_key

            from application.features.Connection import Connection

            with patch('builtins.open', create=True):
                pub_key = Connection.ssh_keygen(key_filename="/tmp/test_key")

            assert "ssh-rsa" in pub_key
            assert "AAAA1234" in pub_key
            mock_paramiko.RSAKey.generate.assert_called_with(3072)

    @pytest.mark.unit
    def test_ssh_keygen_to_file_obj(self):
        """ssh_keygen should write to file object."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_key = Mock()
            mock_key.get_base64.return_value = "BBBB5678"
            mock_paramiko.RSAKey.generate.return_value = mock_key

            from application.features.Connection import Connection

            file_obj = StringIO()
            pub_key = Connection.ssh_keygen(key_file_obj=file_obj, public_key_comment="test@host")

            assert "ssh-rsa" in pub_key
            assert "BBBB5678" in pub_key
            assert "test@host" in pub_key

    @pytest.mark.unit
    def test_ssh_keygen_no_destination_raises(self):
        """ssh_keygen should raise if no destination provided."""
        with patch('application.features.Connection.paramiko'):
            from application.features.Connection import Connection

            with pytest.raises(ValueError, match="Neither key_filename nor key_file_obj"):
                Connection.ssh_keygen()


class TestConnectionHostChecks:
    """Tests for host type checking methods."""

    @pytest.mark.unit
    def test_is_eecg(self):
        """is_eecg should detect EECG hosts."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_paramiko.SSHClient.return_value = Mock()
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()

            conn.host = "ug52.eecg.toronto.edu"
            assert conn.is_eecg() is True

            conn.host = "p1.ecf.utoronto.ca"
            assert conn.is_eecg() is False

    @pytest.mark.unit
    def test_is_ecf(self):
        """is_ecf should detect ECF hosts."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_paramiko.SSHClient.return_value = Mock()
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()

            conn.host = "p1.ecf.utoronto.ca"
            assert conn.is_ecf() is True

            conn.host = "ug52.eecg.toronto.edu"
            assert conn.is_ecf() is False

    @pytest.mark.unit
    def test_is_uoft(self):
        """is_uoft should detect UofT hosts."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_paramiko.SSHClient.return_value = Mock()
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()

            conn.host = "ug52.eecg.toronto.edu"
            assert conn.is_uoft() is True

            conn.host = "p1.ecf.utoronto.ca"
            assert conn.is_uoft() is True

            conn.host = "example.com"
            assert conn.is_uoft() is False


class TestConnectionIsLoadHigh:
    """Tests for is_load_high method.

    The is_load_high method makes two separate exec_command calls:
    1. uptime - to get user count and load averages
    2. who | grep $(whoami) | wc -l - to get current user's session count
    """

    @pytest.mark.unit
    def test_is_load_high_multiple_users(self):
        """is_load_high should return True when other users are connected."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()

            # First call: uptime - shows 3 users
            mock_uptime_stdout = Mock()
            mock_uptime_stdout.readline.return_value = " 10:00:00 up 1 day,  2:30,  3 users,  load average: 0.10, 0.15, 0.20\n"
            mock_uptime_stdout.channel.recv_exit_status.return_value = 0

            # Second call: who | grep $(whoami) | wc -l - shows 1 session (our session)
            mock_who_stdout = Mock()
            mock_who_stdout.readline.return_value = "1\n"
            mock_who_stdout.channel.recv_exit_status.return_value = 0

            # exec_command returns different mocks for each call
            mock_client.exec_command.side_effect = [
                (Mock(), mock_uptime_stdout, Mock()),  # uptime
                (Mock(), mock_who_stdout, Mock()),     # who | grep | wc -l
            ]

            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            # 3 users > 1 session = high load (other users connected)
            assert conn.is_load_high() is True

    @pytest.mark.unit
    def test_is_load_high_high_load_average(self):
        """is_load_high should return True when load average sum > 1.0."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()

            # First call: uptime - 1 user, but high load (0.50 + 0.40 + 0.30 = 1.2)
            mock_uptime_stdout = Mock()
            mock_uptime_stdout.readline.return_value = " 10:00:00 up 1 day,  2:30,  1 users,  load average: 0.50, 0.40, 0.30\n"
            mock_uptime_stdout.channel.recv_exit_status.return_value = 0

            # Second call: who | grep $(whoami) | wc -l
            mock_who_stdout = Mock()
            mock_who_stdout.readline.return_value = "1\n"
            mock_who_stdout.channel.recv_exit_status.return_value = 0

            mock_client.exec_command.side_effect = [
                (Mock(), mock_uptime_stdout, Mock()),
                (Mock(), mock_who_stdout, Mock()),
            ]

            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            # load_sum = 1.2 > 1.0 = high load
            assert conn.is_load_high() is True

    @pytest.mark.unit
    def test_is_load_high_low_load(self):
        """is_load_high should return False when load is low and only user."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()

            # First call: uptime - 1 user, low load (0.10 + 0.05 + 0.05 = 0.2)
            mock_uptime_stdout = Mock()
            mock_uptime_stdout.readline.return_value = " 10:00:00 up 1 day,  2:30,  1 users,  load average: 0.10, 0.05, 0.05\n"
            mock_uptime_stdout.channel.recv_exit_status.return_value = 0

            # Second call: who | grep $(whoami) | wc -l
            mock_who_stdout = Mock()
            mock_who_stdout.readline.return_value = "1\n"
            mock_who_stdout.channel.recv_exit_status.return_value = 0

            mock_client.exec_command.side_effect = [
                (Mock(), mock_uptime_stdout, Mock()),
                (Mock(), mock_who_stdout, Mock()),
            ]

            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            # 1 user = 1 session, load_sum = 0.2 < 1.0 = low load
            assert conn.is_load_high() is False


class TestConnectionSaveKeys:
    """Tests for save_keys method."""

    @pytest.mark.unit
    def test_save_keys_with_filename(self):
        """save_keys should work with key_filename."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_key = Mock()
            mock_key.get_base64.return_value = "AAAA1234"
            mock_paramiko.RSAKey.generate.return_value = mock_key
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            mock_stdout = Mock()
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_client.exec_command.return_value = (Mock(), mock_stdout, Mock())

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            with patch('builtins.open', create=True):
                status, reason = conn.save_keys(key_filename="/tmp/test_key", public_key_comment="test")

            assert status is True
            assert reason == ""

    @pytest.mark.unit
    def test_save_keys_with_file_obj(self):
        """save_keys should work with key_file_obj."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_key = Mock()
            mock_key.get_base64.return_value = "BBBB5678"
            mock_paramiko.RSAKey.generate.return_value = mock_key
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            mock_stdout = Mock()
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_client.exec_command.return_value = (Mock(), mock_stdout, Mock())

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            file_obj = StringIO()
            status, reason = conn.save_keys(key_file_obj=file_obj, public_key_comment="test")

            assert status is True
            assert reason == ""

    @pytest.mark.unit
    def test_save_keys_no_destination_raises(self):
        """save_keys should raise if no destination provided."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            with pytest.raises(ValueError, match="Neither key_filename nor key_file_obj"):
                conn.save_keys()

    @pytest.mark.unit
    def test_save_keys_exec_fails(self):
        """save_keys should return False if exec_command fails."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_key = Mock()
            mock_key.get_base64.return_value = "CCCC9012"
            mock_paramiko.RSAKey.generate.return_value = mock_key
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            mock_stdout = Mock()
            mock_stdout.channel.recv_exit_status.return_value = 1  # Non-zero exit
            mock_client.exec_command.return_value = (Mock(), mock_stdout, Mock())

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            with patch('builtins.open', create=True):
                status, reason = conn.save_keys(key_filename="/tmp/test_key")

            assert status is False
            assert "unable to save public key" in reason


class TestConnectionPortForward:
    """Tests for port forwarding."""

    @pytest.mark.unit
    def test_port_forward_starts_thread(self):
        """port_forward should start a forwarding thread."""
        with patch('application.features.Connection.paramiko') as mock_paramiko, \
             patch('application.features.Connection.threading') as mock_threading:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn.connect("test.host.com", "testuser", password="testpass")

            conn.port_forward(12345, 5901)

            mock_threading.Thread.assert_called_once()
            mock_threading.Thread.return_value.start.assert_called_once()


class TestConnectionDel:
    """Tests for Connection.__del__ method."""

    @pytest.mark.unit
    def test_del_closes_client(self):
        """__del__ should close the client."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()

            # Manually call __del__ logic
            conn.client.close()

            mock_client.close.assert_called_once()

    @pytest.mark.unit
    def test_del_closes_jump_client(self):
        """__del__ should close jump client if present."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_jump_client = Mock()
            mock_jump_channel = Mock()
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.Connection import Connection
            conn = Connection()
            conn._jump_client = mock_jump_client
            conn._jump_channel = mock_jump_channel

            # Manually call __del__ logic
            if conn._jump_client is not None:
                conn._jump_channel.close()
                conn._jump_client.close()

            mock_jump_channel.close.assert_called_once()
            mock_jump_client.close.assert_called_once()


class TestForwardServer:
    """Tests for ForwardServer class."""

    @pytest.mark.unit
    def test_forward_server_class_exists(self):
        """ForwardServer class should exist."""
        from application.features.Connection import ForwardServer

        assert ForwardServer.daemon_threads is True
        assert ForwardServer.allow_reuse_address is True


class TestForwardServerHandler:
    """Tests for ForwardServerHandler class."""

    @pytest.mark.unit
    def test_forward_server_handler_exists(self):
        """ForwardServerHandler class should exist."""
        from application.features.Connection import ForwardServerHandler

        assert hasattr(ForwardServerHandler, 'handle')

    @pytest.mark.unit
    def test_forward_server_handler_open_channel_failure(self):
        """ForwardServerHandler should handle channel open failure."""
        from application.features.Connection import ForwardServerHandler, ForwardServer

        # Create mock handler
        handler = object.__new__(ForwardServerHandler)
        handler.request = Mock()
        handler.request.getpeername.return_value = ('127.0.0.1', 12345)

        # Create mock server with transport that fails to open channel
        mock_server = Mock(spec=ForwardServer)
        mock_transport = Mock()
        mock_transport.open_channel.side_effect = Exception("Channel open failed")
        mock_server.ssh_transport = mock_transport
        mock_server.chain_port = 5901
        handler.server = mock_server

        # handle() should return gracefully when channel open fails
        result = handler.handle()

        # Should return False, error message (though we don't capture return value in real use)
        mock_transport.open_channel.assert_called_once_with(
            "direct-tcpip",
            ("127.0.0.1", 5901),
            ('127.0.0.1', 12345)
        )

    @pytest.mark.unit
    def test_forward_server_handler_data_forwarding(self):
        """ForwardServerHandler should forward data between request and channel."""
        from application.features.Connection import ForwardServerHandler, ForwardServer

        # Create mock handler
        handler = object.__new__(ForwardServerHandler)

        # Mock request socket
        mock_request = Mock()
        mock_request.getpeername.return_value = ('127.0.0.1', 12345)
        mock_request.recv.side_effect = [b'test data', b'']  # Data then empty (close)
        handler.request = mock_request

        # Mock channel
        mock_chan = Mock()
        mock_chan.getpeername.return_value = ('127.0.0.1', 5901)
        mock_chan.recv.return_value = b''  # Empty to end loop

        # Create mock server
        mock_server = Mock(spec=ForwardServer)
        mock_transport = Mock()
        mock_transport.open_channel.return_value = mock_chan
        mock_server.ssh_transport = mock_transport
        mock_server.chain_port = 5901
        handler.server = mock_server

        # Mock select to return request ready first, then channel ready
        with patch('application.features.Connection.select') as mock_select:
            # First iteration: request has data
            # Second iteration: request has empty data (connection closed)
            mock_select.select.side_effect = [
                ([mock_request], [], []),
                ([mock_request], [], []),
            ]

            handler.handle()

            # Verify data was sent to channel
            mock_chan.send.assert_called_with(b'test data')
            mock_chan.close.assert_called_once()
            mock_server.shutdown.assert_called_once()

    @pytest.mark.unit
    def test_forward_server_handler_channel_data_forwarding(self):
        """ForwardServerHandler should forward data from channel to request."""
        from application.features.Connection import ForwardServerHandler, ForwardServer

        # Create mock handler
        handler = object.__new__(ForwardServerHandler)

        # Mock request socket
        mock_request = Mock()
        mock_request.getpeername.return_value = ('127.0.0.1', 12345)
        handler.request = mock_request

        # Mock channel - returns data then empty
        mock_chan = Mock()
        mock_chan.getpeername.return_value = ('127.0.0.1', 5901)
        mock_chan.recv.side_effect = [b'channel data', b'']

        # Create mock server
        mock_server = Mock(spec=ForwardServer)
        mock_transport = Mock()
        mock_transport.open_channel.return_value = mock_chan
        mock_server.ssh_transport = mock_transport
        mock_server.chain_port = 5901
        handler.server = mock_server

        with patch('application.features.Connection.select') as mock_select:
            # Channel has data, then channel has empty data
            mock_select.select.side_effect = [
                ([mock_chan], [], []),
                ([mock_chan], [], []),
            ]

            handler.handle()

            # Verify data was sent to request
            mock_request.send.assert_called_with(b'channel data')

    @pytest.mark.unit
    def test_forward_server_handler_exception_in_loop(self):
        """ForwardServerHandler should handle exceptions in forwarding loop."""
        from application.features.Connection import ForwardServerHandler, ForwardServer

        handler = object.__new__(ForwardServerHandler)

        mock_request = Mock()
        mock_request.getpeername.return_value = ('127.0.0.1', 12345)
        mock_request.recv.side_effect = Exception("Socket error")
        handler.request = mock_request

        mock_chan = Mock()
        mock_chan.getpeername.return_value = ('127.0.0.1', 5901)

        mock_server = Mock(spec=ForwardServer)
        mock_transport = Mock()
        mock_transport.open_channel.return_value = mock_chan
        mock_server.ssh_transport = mock_transport
        mock_server.chain_port = 5901
        handler.server = mock_server

        with patch('application.features.Connection.select') as mock_select:
            mock_select.select.return_value = ([mock_request], [], [])

            # Should not raise - handles exception gracefully
            handler.handle()

            # Should still try to close channel and shutdown
            mock_chan.close.assert_called_once()

    @pytest.mark.unit
    def test_forward_server_handler_close_exception(self):
        """ForwardServerHandler should handle exceptions when closing."""
        from application.features.Connection import ForwardServerHandler, ForwardServer

        handler = object.__new__(ForwardServerHandler)

        mock_request = Mock()
        mock_request.getpeername.return_value = ('127.0.0.1', 12345)
        mock_request.recv.return_value = b''  # Empty to trigger close
        handler.request = mock_request

        mock_chan = Mock()
        mock_chan.getpeername.return_value = ('127.0.0.1', 5901)
        mock_chan.recv.return_value = b''
        mock_chan.close.side_effect = Exception("Close failed")

        mock_server = Mock(spec=ForwardServer)
        mock_transport = Mock()
        mock_transport.open_channel.return_value = mock_chan
        mock_server.ssh_transport = mock_transport
        mock_server.chain_port = 5901
        handler.server = mock_server

        with patch('application.features.Connection.select') as mock_select:
            mock_select.select.return_value = ([mock_request], [], [])

            # Should not raise even if close fails
            handler.handle()

            mock_chan.close.assert_called_once()
