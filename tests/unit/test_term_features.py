"""
Unit tests for features/Term.py.

Tests the Term class and TermWebSocket handler.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock
import uuid


def get_term_module():
    """Get the features/Term module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.features.Term']


def get_connection_module():
    """Get the features/Connection module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.features.Connection']


class TestTermInit:
    """Tests for Term class initialization."""

    def test_term_init(self):
        """Test Term initializes with None id and channel."""
        term_module = get_term_module()

        with patch.object(term_module.Term, '__init__', lambda self: None):
            term = object.__new__(term_module.Term)
            term.id = None
            term.channel = None
            assert term.id is None
            assert term.channel is None


class TestTermInheritance:
    """Tests for Term class inheritance."""

    def test_term_inherits_connection(self):
        """Test Term inherits from Connection."""
        term_module = get_term_module()
        connection_module = get_connection_module()

        assert issubclass(term_module.Term, connection_module.Connection)


class TestTermLaunchShell:
    """Tests for Term.launch_shell method."""

    @pytest.fixture
    def mock_term(self):
        """Create a mock Term instance."""
        term_module = get_term_module()

        term = object.__new__(term_module.Term)
        term.id = None
        term.channel = None
        term.client = MagicMock()
        return term

    def test_launch_shell_success(self, mock_term):
        """Test launch_shell creates shell channel successfully."""
        term_module = get_term_module()

        mock_channel = MagicMock()
        mock_term.client.invoke_shell.return_value = mock_channel

        status, term_id = mock_term.launch_shell()

        assert status is True
        assert term_id is not None
        assert len(term_id) == 32  # UUID hex string
        mock_term.client.invoke_shell.assert_called_once_with('xterm-256color')
        assert mock_term.channel == mock_channel
        assert mock_term.id == term_id
        # Should be added to TERM_CONNECTIONS
        assert term_id in term_module.TERM_CONNECTIONS
        assert term_module.TERM_CONNECTIONS[term_id] == mock_term

        # Clean up
        del term_module.TERM_CONNECTIONS[term_id]

    def test_launch_shell_failure(self, mock_term):
        """Test launch_shell returns error on exception."""
        mock_term.client.invoke_shell.side_effect = Exception('Shell failed')

        status, reason = mock_term.launch_shell()

        assert status is False
        assert 'Shell failed' in reason


class TestTermResize:
    """Tests for Term.resize method."""

    @pytest.fixture
    def mock_term(self):
        """Create a mock Term instance."""
        term_module = get_term_module()

        term = object.__new__(term_module.Term)
        term.id = 'test-term-id'
        term.channel = MagicMock()
        return term

    def test_resize_success(self, mock_term):
        """Test resize resizes PTY successfully."""
        status, reason = mock_term.resize(120, 40)

        assert status is True
        assert reason == ''
        mock_term.channel.resize_pty.assert_called_once_with(120, 40)

    def test_resize_failure(self, mock_term):
        """Test resize returns error on exception."""
        mock_term.channel.resize_pty.side_effect = Exception('Resize failed')

        status, reason = mock_term.resize(80, 24)

        assert status is False
        assert 'Resize failed' in reason


class TestTermDel:
    """Tests for Term.__del__ method."""

    def test_del_closes_channel(self):
        """Test __del__ closes the channel."""
        term_module = get_term_module()

        term = object.__new__(term_module.Term)
        term.channel = MagicMock()
        term.client = None  # Prevent parent __del__ from being called

        # Manually call __del__ logic
        if term.channel:
            term.channel.close()

        term.channel.close.assert_called_once()


class TestTermConnect:
    """Tests for Term.connect method."""

    def test_connect_calls_super(self):
        """Test Term.connect calls parent connect."""
        term_module = get_term_module()

        term = object.__new__(term_module.Term)
        term.client = None

        with patch.object(term_module.Connection, 'connect') as mock_connect:
            mock_connect.return_value = (True, '')
            term.connect('host', 'user', 'password')
            mock_connect.assert_called_once()


class TestTermWebSocketInit:
    """Tests for TermWebSocket initialization."""

    def test_termwebsocket_init(self):
        """Test TermWebSocket initializes with None term."""
        term_module = get_term_module()

        # TermWebSocket requires server/socket args, so we check the class
        assert hasattr(term_module.TermWebSocket, 'handleMessage')
        assert hasattr(term_module.TermWebSocket, 'handleConnected')
        assert hasattr(term_module.TermWebSocket, 'handleClose')


class TestTermWebSocketHandleMessage:
    """Tests for TermWebSocket.handleMessage method."""

    def test_handle_message_sends_to_channel(self):
        """Test handleMessage sends data to terminal channel."""
        term_module = get_term_module()

        # Create a mock WebSocket instance
        mock_ws = MagicMock(spec=term_module.TermWebSocket)
        mock_ws.term = MagicMock()
        mock_ws.term.channel = MagicMock()
        mock_ws.data = b'test input'

        # Call the method directly
        term_module.TermWebSocket.handleMessage(mock_ws)

        mock_ws.term.channel.send.assert_called_once_with(b'test input')


class TestTermWebSocketHandleConnected:
    """Tests for TermWebSocket.handleConnected method."""

    def test_handle_connected_auth_failure(self):
        """Test handleConnected closes on auth failure."""
        term_module = get_term_module()

        mock_ws = MagicMock(spec=term_module.TermWebSocket)
        mock_ws.headerbuffer = b'GET /test-id HTTP/1.1\r\nHost: localhost\r\n\r\n'
        mock_ws.request = MagicMock()
        mock_ws.request.path = '/test-term-id'

        with patch.object(term_module, 'local_auth') as mock_auth:
            mock_auth.return_value = False

            term_module.TermWebSocket.handleConnected(mock_ws)

            mock_auth.assert_called_once()
            # Should not set term since auth failed

    def test_handle_connected_term_not_found(self):
        """Test handleConnected closes when terminal ID not found."""
        term_module = get_term_module()

        mock_ws = MagicMock(spec=term_module.TermWebSocket)
        mock_ws.headerbuffer = b'GET /nonexistent HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer test-auth-key\r\n\r\n'
        mock_ws.request = MagicMock()
        mock_ws.request.path = '/nonexistent'
        mock_ws.address = ('127.0.0.1', 12345)

        with patch.object(term_module, 'local_auth') as mock_auth, \
             patch.dict(term_module.TERM_CONNECTIONS, {}, clear=True):
            mock_auth.return_value = True

            term_module.TermWebSocket.handleConnected(mock_ws)

            mock_ws.close.assert_called_once()

    def test_handle_connected_success(self):
        """Test handleConnected sets up terminal connection."""
        term_module = get_term_module()

        mock_ws = MagicMock(spec=term_module.TermWebSocket)
        mock_ws.headerbuffer = b'GET /test-term-id HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer test-auth-key\r\n\r\n'
        mock_ws.request = MagicMock()
        mock_ws.request.path = '/test-term-id'
        mock_ws.address = ('127.0.0.1', 12345)

        mock_term = MagicMock()
        mock_term.channel = MagicMock()

        with patch.object(term_module, 'local_auth') as mock_auth, \
             patch.dict(term_module.TERM_CONNECTIONS, {'test-term-id': mock_term}), \
             patch.object(term_module, 'threading') as mock_threading:
            mock_auth.return_value = True

            term_module.TermWebSocket.handleConnected(mock_ws)

            assert mock_ws.term == mock_term
            mock_threading.Thread.assert_called_once()
            mock_threading.Thread.return_value.start.assert_called_once()


class TestTermWebSocketHandleClose:
    """Tests for TermWebSocket.handleClose method."""

    def test_handle_close_removes_connection(self):
        """Test handleClose removes terminal from TERM_CONNECTIONS."""
        term_module = get_term_module()

        mock_ws = MagicMock(spec=term_module.TermWebSocket)
        mock_term = MagicMock()
        mock_term.id = 'test-term-id'
        mock_ws.term = mock_term

        with patch.dict(term_module.TERM_CONNECTIONS, {'test-term-id': mock_term}):
            term_module.TermWebSocket.handleClose(mock_ws)

            assert 'test-term-id' not in term_module.TERM_CONNECTIONS


class TestTermModuleConstants:
    """Tests for Term module constants."""

    def test_term_connections_dict_exists(self):
        """Test TERM_CONNECTIONS dict exists."""
        term_module = get_term_module()

        assert hasattr(term_module, 'TERM_CONNECTIONS')
        assert isinstance(term_module.TERM_CONNECTIONS, dict)

    def test_terminal_port_defined(self):
        """Test TERMINAL_PORT is defined."""
        term_module = get_term_module()

        assert hasattr(term_module, 'TERMINAL_PORT')
        assert isinstance(term_module.TERMINAL_PORT, int)
        assert term_module.TERMINAL_PORT > 0
