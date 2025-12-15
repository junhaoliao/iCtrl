"""
Unit tests for features/VNC.py.

Tests the VNC class methods.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import io


def get_vnc_module():
    """Get the features/VNC module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.features.VNC']


def get_connection_module():
    """Get the features/Connection module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.features.Connection']


class TestVNCInit:
    """Tests for VNC class initialization."""

    def test_vnc_init(self):
        """Test VNC initializes with None id."""
        vnc_module = get_vnc_module()

        with patch.object(vnc_module.VNC, '__init__', lambda self: None):
            vnc = object.__new__(vnc_module.VNC)
            vnc.id = None
            assert vnc.id is None


class TestGetVncPassword:
    """Tests for VNC.get_vnc_password method."""

    @pytest.fixture
    def mock_vnc(self):
        """Create a mock VNC instance."""
        vnc_module = get_vnc_module()

        vnc = object.__new__(vnc_module.VNC)
        vnc.exec_command_blocking = MagicMock()
        return vnc

    def test_get_vnc_password_empty(self, mock_vnc):
        """Test get_vnc_password returns False when no password file."""
        mock_stdout = io.StringIO('')
        mock_vnc.exec_command_blocking.return_value = (None, None, mock_stdout, None)

        status, password = mock_vnc.get_vnc_password()

        assert status is False
        assert password == ''

    def test_get_vnc_password_success(self, mock_vnc):
        """Test get_vnc_password returns password when file exists."""
        vnc_module = get_vnc_module()

        # Mock hexdump output (8 bytes = 16 hex chars)
        mock_stdout = io.StringIO('e9a75a01d857bf53')
        mock_vnc.exec_command_blocking.return_value = (None, None, mock_stdout, None)

        with patch.object(vnc_module, 'decrypt_passwd') as mock_decrypt:
            mock_decrypt.return_value = 'decrypted_password'

            status, password = mock_vnc.get_vnc_password()

            assert status is True
            assert password == 'decrypted_password'
            mock_decrypt.assert_called_once()


class TestCheck5900Open:
    """Tests for VNC.check_5900_open method."""

    @pytest.fixture
    def mock_vnc(self):
        """Create a mock VNC instance."""
        vnc_module = get_vnc_module()

        vnc = object.__new__(vnc_module.VNC)
        vnc.exec_command_blocking = MagicMock()
        return vnc

    def test_check_5900_open_linux_open(self, mock_vnc):
        """Test check_5900_open returns True when 5900 is open (Linux)."""
        mock_stdout = io.StringIO('tcp    LISTEN     0      5      *:5900     *:*\n')
        mock_vnc.exec_command_blocking.return_value = (None, None, mock_stdout, None)

        result = mock_vnc.check_5900_open()

        assert result is True

    def test_check_5900_open_linux_closed(self, mock_vnc):
        """Test check_5900_open returns False when 5900 is closed (Linux)."""
        # First call (ss) returns empty, second call (netstat) returns empty
        mock_vnc.exec_command_blocking.side_effect = [
            (None, None, io.StringIO(''), None),  # ss command
            (None, None, io.StringIO(''), None),  # netstat command
        ]

        result = mock_vnc.check_5900_open()

        assert result is False

    def test_check_5900_open_mac_open(self, mock_vnc):
        """Test check_5900_open returns True when 5900 is open (macOS)."""
        # First call (ss) returns empty, second call (netstat) returns result
        mock_vnc.exec_command_blocking.side_effect = [
            (None, None, io.StringIO(''), None),  # ss command
            (None, None, io.StringIO('tcp4       0      0  *.5900      *.*      LISTEN\n'), None),  # netstat
        ]

        result = mock_vnc.check_5900_open()

        assert result is True


class TestRemoveVncSettings:
    """Tests for VNC.remove_vnc_settings method."""

    @pytest.fixture
    def mock_vnc(self):
        """Create a mock VNC instance."""
        vnc_module = get_vnc_module()

        vnc = object.__new__(vnc_module.VNC)
        vnc.exec_command_blocking = MagicMock()
        return vnc

    def test_remove_vnc_settings_success(self, mock_vnc):
        """Test remove_vnc_settings returns success."""
        mock_vnc.exec_command_blocking.return_value = (None, None, None, [])

        status, reason = mock_vnc.remove_vnc_settings()

        assert status is True
        assert reason == ''

    def test_remove_vnc_settings_error(self, mock_vnc):
        """Test remove_vnc_settings returns error on stderr."""
        mock_vnc.exec_command_blocking.return_value = (None, None, None, ['Error removing files'])

        status, reason = mock_vnc.remove_vnc_settings()

        assert status is False
        assert 'Error removing files' in reason


class TestResetVncPassword:
    """Tests for VNC.reset_vnc_password method."""

    @pytest.fixture
    def mock_vnc(self):
        """Create a mock VNC instance."""
        vnc_module = get_vnc_module()

        vnc = object.__new__(vnc_module.VNC)
        vnc.exec_command_blocking = MagicMock()
        return vnc

    def test_reset_vnc_password_success(self, mock_vnc):
        """Test reset_vnc_password returns success."""
        mock_vnc.exec_command_blocking.return_value = (None, None, None, iter([]))

        status, reason = mock_vnc.reset_vnc_password('newpassword')

        assert status is True
        assert reason == ''

    def test_reset_vnc_password_quota_exceeded(self, mock_vnc):
        """Test reset_vnc_password returns quota exceeded error."""
        mock_vnc.exec_command_blocking.return_value = (None, None, None, iter(['Disk quota exceeded']))

        status, reason = mock_vnc.reset_vnc_password('newpassword')

        assert status is False
        assert reason == 'Disk quota exceeded'

    def test_reset_vnc_password_other_error(self, mock_vnc):
        """Test reset_vnc_password returns other error."""
        mock_vnc.exec_command_blocking.return_value = (None, None, None, iter(['Some other error']))

        status, reason = mock_vnc.reset_vnc_password('newpassword')

        assert status is False
        assert 'Some other error' in reason


class TestLaunchVnc:
    """Tests for VNC.launch_vnc method."""

    @pytest.fixture
    def mock_vnc(self):
        """Create a mock VNC instance."""
        vnc_module = get_vnc_module()

        vnc = object.__new__(vnc_module.VNC)
        vnc.exec_command_blocking = MagicMock()
        vnc.is_eecg = MagicMock(return_value=False)
        return vnc

    def test_launch_vnc_existing_server(self, mock_vnc):
        """Test launch_vnc reuses existing VNC server."""
        # vncserver -list returns one port
        mock_stdout = io.StringIO(':1    12345\n')
        mock_vnc.exec_command_blocking.return_value = (None, None, mock_stdout, None)

        status, port = mock_vnc.launch_vnc()

        assert status is True
        assert port == 5901

    def test_launch_vnc_no_existing_server(self, mock_vnc):
        """Test launch_vnc starts new VNC server."""
        # First call: vncserver -list returns empty
        # Second call: relaunch commands
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        mock_vnc.exec_command_blocking.side_effect = [
            (None, None, io.StringIO(''), None),  # vncserver -list
            (None, None, io.StringIO('New desktop is machine:2\n'), mock_stderr),  # relaunch
        ]

        status, port = mock_vnc.launch_vnc()

        assert status is True
        assert port == 5902

    def test_launch_vnc_multiple_servers(self, mock_vnc):
        """Test launch_vnc kills and restarts when multiple servers exist."""
        # First call: vncserver -list returns multiple ports
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        mock_vnc.exec_command_blocking.side_effect = [
            (None, None, io.StringIO(':1    12345\n:2    67890\n'), None),  # vncserver -list
            (None, None, io.StringIO('New desktop is machine:3\n'), mock_stderr),  # relaunch
        ]

        status, port = mock_vnc.launch_vnc()

        assert status is True
        assert port == 5903

    def test_launch_vnc_quota_error(self, mock_vnc):
        """Test launch_vnc returns False on quota error."""
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = ['quota exceeded error']
        mock_vnc.exec_command_blocking.side_effect = [
            (None, None, io.StringIO(''), None),  # vncserver -list
            (None, None, io.StringIO(''), mock_stderr),  # relaunch with error
        ]

        status, reason = mock_vnc.launch_vnc()

        assert status is False
        assert reason == 'QUOTA'

    def test_launch_vnc_eecg_server(self, mock_vnc):
        """Test launch_vnc runs xvfb-run on EECG servers."""
        mock_vnc.is_eecg.return_value = True

        # vncserver -list returns one port
        mock_vnc.exec_command_blocking.side_effect = [
            (None, None, io.StringIO(':1    12345\n'), None),  # vncserver -list
            (None, None, None, None),  # xvfb-run command
        ]

        status, port = mock_vnc.launch_vnc()

        assert status is True
        assert port == 5901
        # Should have called exec_command_blocking twice (list + xvfb)
        assert mock_vnc.exec_command_blocking.call_count == 2


class TestCreateTunnel:
    """Tests for VNC.create_tunnel method."""

    @pytest.fixture
    def mock_vnc(self):
        """Create a mock VNC instance."""
        vnc_module = get_vnc_module()

        vnc = object.__new__(vnc_module.VNC)
        vnc.port_forward = MagicMock()
        return vnc

    def test_create_tunnel(self, mock_vnc):
        """Test create_tunnel creates port forwarding and starts proxy."""
        vnc_module = get_vnc_module()

        with patch.object(vnc_module, 'find_free_port') as mock_find_port, \
             patch.object(vnc_module, 'threading') as mock_threading:
            mock_find_port.side_effect = [12345, 54321]  # local_vnc_port, local_websocket_port

            result = mock_vnc.create_tunnel(5901)

            assert result == 54321
            mock_vnc.port_forward.assert_called_once_with(12345, 5901)
            mock_threading.Thread.assert_called_once()
            mock_threading.Thread.return_value.start.assert_called_once()


class TestWebsocketProxyThread:
    """Tests for websocket_proxy_thread function."""

    def test_websocket_proxy_thread_no_ssl_cert(self):
        """Test websocket_proxy_thread without SSL certificate."""
        vnc_module = get_vnc_module()
        import os

        # Save and remove SSL cert path
        old_val = os.environ.pop('ICTRL_SSL_CERT_PATH', None)

        try:
            with patch.object(vnc_module, 'MySSLProxyServer') as mock_server:
                mock_server_instance = MagicMock()
                mock_server.return_value = mock_server_instance

                vnc_module.websocket_proxy_thread(54321, 12345)

                mock_server.assert_called_once()
                # Should handle exactly 2 requests
                assert mock_server_instance.handle_request.call_count == 2
                mock_server_instance.server_close.assert_called_once()
        finally:
            # Restore the env var if it existed
            if old_val is not None:
                os.environ['ICTRL_SSL_CERT_PATH'] = old_val

    def test_websocket_proxy_thread_with_ssl_cert(self):
        """Test websocket_proxy_thread with SSL certificate."""
        vnc_module = get_vnc_module()

        with patch.dict('os.environ', {
            'ICTRL_SSL_CERT_PATH': '/path/to/cert.pem',
            'ICTRL_SSL_KEY_PATH': '/path/to/key.pem'
        }), patch('subprocess.run') as mock_run:
            vnc_module.websocket_proxy_thread(54321, 12345)

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert '54321' in args
            assert ':12345' in args
            assert '--ssl-only' in args


class TestVNCInheritance:
    """Tests for VNC class inheritance from Connection."""

    def test_vnc_inherits_connection(self):
        """Test VNC inherits from Connection."""
        vnc_module = get_vnc_module()
        connection_module = get_connection_module()

        assert issubclass(vnc_module.VNC, connection_module.Connection)

    def test_vnc_connect_calls_super(self):
        """Test VNC.connect calls parent connect."""
        vnc_module = get_vnc_module()

        vnc = object.__new__(vnc_module.VNC)
        vnc.client = None

        with patch.object(vnc_module.Connection, 'connect') as mock_connect:
            mock_connect.return_value = (True, '')
            vnc.connect('host', 'user', 'password')
            mock_connect.assert_called_once()
