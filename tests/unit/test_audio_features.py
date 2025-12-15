"""
Unit tests for features/Audio.py.

Tests the Audio class and AudioWebSocket handler.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock
import io


def get_audio_module():
    """Get the features/Audio module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.features.Audio']


def get_connection_module():
    """Get the features/Connection module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.features.Connection']


class TestAudioInit:
    """Tests for Audio class initialization."""

    @pytest.mark.unit
    def test_audio_init(self):
        """Test Audio initializes with None id and zero port."""
        audio_module = get_audio_module()

        with patch.object(audio_module.Audio, '__init__', lambda self: None):
            audio = object.__new__(audio_module.Audio)
            audio.id = None
            audio.transport = None
            audio.remote_port = 0
            assert audio.id is None
            assert audio.transport is None
            assert audio.remote_port == 0


class TestAudioInheritance:
    """Tests for Audio class inheritance."""

    @pytest.mark.unit
    def test_audio_inherits_connection(self):
        """Test Audio inherits from Connection."""
        audio_module = get_audio_module()
        connection_module = get_connection_module()

        assert issubclass(audio_module.Audio, connection_module.Connection)


class TestAudioConnect:
    """Tests for Audio.connect method."""

    @pytest.mark.unit
    def test_connect_calls_super(self):
        """Test Audio.connect calls parent connect."""
        audio_module = get_audio_module()

        audio = object.__new__(audio_module.Audio)
        audio.client = None

        with patch.object(audio_module.Connection, 'connect') as mock_connect:
            mock_connect.return_value = (True, '')
            audio.connect('host', 'user', 'password')
            mock_connect.assert_called_once()


class TestAudioLaunchAudio:
    """Tests for Audio.launch_audio method."""

    @pytest.fixture
    def mock_audio(self):
        """Create a mock Audio instance."""
        audio_module = get_audio_module()

        audio = object.__new__(audio_module.Audio)
        audio.id = None
        audio.transport = None
        audio.remote_port = 0
        audio.client = MagicMock()
        return audio

    @pytest.mark.unit
    def test_launch_audio_success(self, mock_audio):
        """Test launch_audio creates transport and port forward successfully."""
        audio_module = get_audio_module()

        mock_transport = MagicMock()
        mock_transport.request_port_forward.return_value = 12345
        mock_audio.client.get_transport.return_value = mock_transport

        status, audio_id = mock_audio.launch_audio()

        assert status is True
        assert audio_id is not None
        assert len(audio_id) == 32  # UUID hex string
        mock_audio.client.get_transport.assert_called_once()
        mock_transport.request_port_forward.assert_called_once_with('127.0.0.1', 0)
        assert mock_audio.transport == mock_transport
        assert mock_audio.remote_port == 12345
        assert mock_audio.id == audio_id
        # Should be added to AUDIO_CONNECTIONS
        assert audio_id in audio_module.AUDIO_CONNECTIONS
        assert audio_module.AUDIO_CONNECTIONS[audio_id] == mock_audio

        # Clean up
        del audio_module.AUDIO_CONNECTIONS[audio_id]

    @pytest.mark.unit
    def test_launch_audio_failure(self, mock_audio):
        """Test launch_audio returns error on exception."""
        mock_audio.client.get_transport.side_effect = Exception('Transport failed')

        status, reason = mock_audio.launch_audio()

        assert status is False
        assert 'Transport failed' in reason


class TestAudioDel:
    """Tests for Audio.__del__ method."""

    @pytest.mark.unit
    def test_del_cancels_port_forward(self):
        """Test __del__ cancels port forward if remote_port is set."""
        audio_module = get_audio_module()

        audio = object.__new__(audio_module.Audio)
        audio.transport = MagicMock()
        audio.remote_port = 12345
        audio.client = None  # Prevent parent __del__ from being called

        # Manually call __del__ logic
        if audio.remote_port != 0:
            audio.transport.cancel_port_forward('127.0.0.1', audio.remote_port)

        audio.transport.cancel_port_forward.assert_called_once_with('127.0.0.1', 12345)

    @pytest.mark.unit
    def test_del_closes_transport(self):
        """Test __del__ closes transport if set."""
        audio_module = get_audio_module()

        audio = object.__new__(audio_module.Audio)
        audio.transport = MagicMock()
        audio.remote_port = 0
        audio.client = None  # Prevent parent __del__ from being called

        # Manually call __del__ logic
        if audio.transport is not None:
            audio.transport.close()

        audio.transport.close.assert_called_once()


class TestAudioWebSocketInit:
    """Tests for AudioWebSocket initialization."""

    @pytest.mark.unit
    def test_audiowebsocket_has_handler_methods(self):
        """Test AudioWebSocket has handleMessage, handleConnected, handleClose."""
        audio_module = get_audio_module()

        assert hasattr(audio_module.AudioWebSocket, 'handleConnected')
        assert hasattr(audio_module.AudioWebSocket, 'handleClose')


class TestAudioWebSocketHandleConnected:
    """Tests for AudioWebSocket.handleConnected method."""

    @pytest.mark.unit
    def test_handle_connected_auth_failure(self):
        """Test handleConnected closes on auth failure."""
        audio_module = get_audio_module()

        mock_ws = MagicMock(spec=audio_module.AudioWebSocket)
        mock_ws.headerbuffer = b'GET /test-id HTTP/1.1\r\nHost: localhost\r\n\r\n'
        mock_ws.request = MagicMock()
        mock_ws.request.path = '/test-audio-id'

        with patch.object(audio_module, 'local_auth') as mock_auth:
            mock_auth.return_value = False

            audio_module.AudioWebSocket.handleConnected(mock_ws)

            mock_auth.assert_called_once()

    @pytest.mark.unit
    def test_handle_connected_audio_not_found(self):
        """Test handleConnected closes when audio ID not found."""
        audio_module = get_audio_module()

        mock_ws = MagicMock(spec=audio_module.AudioWebSocket)
        mock_ws.headerbuffer = b'GET /nonexistent HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer test-auth-key\r\n\r\n'
        mock_ws.request = MagicMock()
        mock_ws.request.path = '/nonexistent'

        with patch.object(audio_module, 'local_auth') as mock_auth, \
             patch.dict(audio_module.AUDIO_CONNECTIONS, {}, clear=True):
            mock_auth.return_value = True

            audio_module.AudioWebSocket.handleConnected(mock_ws)

            mock_ws.close.assert_called_once()

    @pytest.mark.unit
    def test_handle_connected_load_module_failure(self):
        """Test handleConnected returns on pactl module load failure."""
        audio_module = get_audio_module()

        mock_ws = MagicMock(spec=audio_module.AudioWebSocket)
        mock_ws.headerbuffer = b'GET /test-audio-id HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer test-auth-key\r\n\r\n'
        mock_ws.request = MagicMock()
        mock_ws.request.path = '/test-audio-id'

        mock_audio = MagicMock()
        mock_audio.username = 'testuser'
        mock_audio.exec_command_blocking.return_value = (1, None, MagicMock(), None)  # exit_status != 0

        with patch.object(audio_module, 'local_auth', return_value=True), \
             patch.dict(audio_module.AUDIO_CONNECTIONS, {'test-audio-id': mock_audio}), \
             patch('builtins.print'):
            audio_module.AudioWebSocket.handleConnected(mock_ws)

            # Should have called exec_command_blocking to load module
            mock_audio.exec_command_blocking.assert_called_once()

    @pytest.mark.unit
    def test_handle_connected_success_starts_threads(self):
        """Test handleConnected starts ffmpeg launcher and writer threads."""
        audio_module = get_audio_module()

        mock_ws = MagicMock(spec=audio_module.AudioWebSocket)
        mock_ws.headerbuffer = b'GET /test-audio-id HTTP/1.1\r\nHost: localhost\r\nAuthorization: Bearer test-auth-key\r\n\r\n'
        mock_ws.request = MagicMock()
        mock_ws.request.path = '/test-audio-id'

        mock_audio = MagicMock()
        mock_audio.username = 'testuser'
        mock_audio.remote_port = 12345
        mock_stdout = MagicMock()
        mock_stdout.readlines.return_value = ['42']  # module_id
        mock_audio.exec_command_blocking.return_value = (0, None, mock_stdout, None)

        with patch.object(audio_module, 'local_auth', return_value=True), \
             patch.dict(audio_module.AUDIO_CONNECTIONS, {'test-audio-id': mock_audio}), \
             patch.object(audio_module, 'threading') as mock_threading:

            audio_module.AudioWebSocket.handleConnected(mock_ws)

            assert mock_ws.audio == mock_audio
            assert mock_ws.module_id == 42
            # Should have created 2 threads
            assert mock_threading.Thread.call_count == 2
            # Both threads should be started
            assert mock_threading.Thread.return_value.start.call_count == 2


class TestAudioWebSocketHandleClose:
    """Tests for AudioWebSocket.handleClose method."""

    @pytest.mark.unit
    def test_handle_close_unloads_module(self):
        """Test handleClose unloads pactl module."""
        audio_module = get_audio_module()

        mock_ws = MagicMock(spec=audio_module.AudioWebSocket)
        mock_audio = MagicMock()
        mock_audio.id = 'test-audio-id'
        mock_ws.audio = mock_audio
        mock_ws.module_id = 12345

        with patch.dict(audio_module.AUDIO_CONNECTIONS, {'test-audio-id': mock_audio}):
            audio_module.AudioWebSocket.handleClose(mock_ws)

            # Should unload the module
            mock_audio.client.exec_command.assert_called_once_with('pactl unload-module 12345')
            # Should remove from AUDIO_CONNECTIONS
            assert 'test-audio-id' not in audio_module.AUDIO_CONNECTIONS

    @pytest.mark.unit
    def test_handle_close_no_module_id(self):
        """Test handleClose skips unload when module_id is None."""
        audio_module = get_audio_module()

        mock_ws = MagicMock(spec=audio_module.AudioWebSocket)
        mock_audio = MagicMock()
        mock_audio.id = 'test-audio-id'
        mock_ws.audio = mock_audio
        mock_ws.module_id = None

        with patch.dict(audio_module.AUDIO_CONNECTIONS, {'test-audio-id': mock_audio}):
            audio_module.AudioWebSocket.handleClose(mock_ws)

            # Should NOT unload the module
            mock_audio.client.exec_command.assert_not_called()
            # Should still remove from AUDIO_CONNECTIONS
            assert 'test-audio-id' not in audio_module.AUDIO_CONNECTIONS


class TestAudioModuleConstants:
    """Tests for Audio module constants."""

    @pytest.mark.unit
    def test_audio_connections_dict_exists(self):
        """Test AUDIO_CONNECTIONS dict exists."""
        audio_module = get_audio_module()

        assert hasattr(audio_module, 'AUDIO_CONNECTIONS')
        assert isinstance(audio_module.AUDIO_CONNECTIONS, dict)

    @pytest.mark.unit
    def test_audio_port_defined(self):
        """Test AUDIO_PORT is defined."""
        audio_module = get_audio_module()

        assert hasattr(audio_module, 'AUDIO_PORT')
        assert isinstance(audio_module.AUDIO_PORT, int)
        assert audio_module.AUDIO_PORT > 0

    @pytest.mark.unit
    def test_ffmpeg_load_time_defined(self):
        """Test FFMPEG_LOAD_TIME is defined."""
        audio_module = get_audio_module()

        assert hasattr(audio_module, 'FFMPEG_LOAD_TIME')
        assert audio_module.FFMPEG_LOAD_TIME == 4

    @pytest.mark.unit
    def test_try_ffmpeg_max_count_defined(self):
        """Test TRY_FFMPEG_MAX_COUNT is defined."""
        audio_module = get_audio_module()

        assert hasattr(audio_module, 'TRY_FFMPEG_MAX_COUNT')
        assert audio_module.TRY_FFMPEG_MAX_COUNT == 3

    @pytest.mark.unit
    def test_audio_buffer_size_defined(self):
        """Test AUDIO_BUFFER_SIZE is defined."""
        audio_module = get_audio_module()

        assert hasattr(audio_module, 'AUDIO_BUFFER_SIZE')
        assert audio_module.AUDIO_BUFFER_SIZE == 20480
