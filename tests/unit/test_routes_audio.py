"""
Unit tests for routes/audio.py.

Tests the audio streaming API endpoint.
"""

import sys
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock


def get_audio_routes_module():
    """Get the routes/audio module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.routes.audio']


def get_codes_module():
    """Get the codes module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.codes']


class TestStartAudio:
    """Tests for /api/audio endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from application import api
        flask_app = Flask(__name__)
        flask_app.register_blueprint(api, url_prefix='/api')
        flask_app.config['TESTING'] = True
        with flask_app.test_client() as client:
            yield client

    @pytest.mark.unit
    def test_start_audio_success(self, client):
        """POST /api/audio returns port and audio_id on success."""
        audio_routes = get_audio_routes_module()

        with patch.object(audio_routes, 'create_connection') as mock_create:
            mock_audio = MagicMock()
            mock_audio.launch_audio.return_value = (True, 'test-audio-id')
            mock_audio.id = 'test-audio-id'
            mock_create.return_value = (mock_audio, '')

            response = client.post(
                '/api/audio',
                json={'session_id': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert 'port' in data
            assert 'audio_id' in data
            assert data['audio_id'] == 'test-audio-id'

    @pytest.mark.unit
    def test_start_audio_connection_failure(self, client):
        """POST /api/audio returns 403 when connection fails."""
        audio_routes = get_audio_routes_module()

        with patch.object(audio_routes, 'create_connection') as mock_create:
            mock_create.return_value = (None, 'Connection failed')

            response = client.post(
                '/api/audio',
                json={'session_id': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            assert b'Connection failed' in response.data

    @pytest.mark.unit
    def test_start_audio_launch_failure(self, client):
        """POST /api/audio returns 403 when launch_audio fails."""
        audio_routes = get_audio_routes_module()

        with patch.object(audio_routes, 'create_connection') as mock_create:
            mock_audio = MagicMock()
            mock_audio.launch_audio.return_value = (False, 'Failed to launch audio')
            mock_create.return_value = (mock_audio, '')

            response = client.post(
                '/api/audio',
                json={'session_id': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            assert b'Failed to launch audio' in response.data

    @pytest.mark.unit
    def test_start_audio_uses_connection_type_audio(self, client):
        """POST /api/audio calls create_connection with ConnectionType.AUDIO."""
        audio_routes = get_audio_routes_module()
        codes = get_codes_module()

        with patch.object(audio_routes, 'create_connection') as mock_create:
            mock_audio = MagicMock()
            mock_audio.launch_audio.return_value = (True, 'test-audio-id')
            mock_audio.id = 'test-audio-id'
            mock_create.return_value = (mock_audio, '')

            client.post(
                '/api/audio',
                json={'session_id': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            mock_create.assert_called_once_with('test-session', codes.ConnectionType.AUDIO)
