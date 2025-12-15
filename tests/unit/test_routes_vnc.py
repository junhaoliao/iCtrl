"""
Unit tests for routes/vnc.py.

Tests the VNC route handlers.
"""

import sys
import json
import pytest
from unittest.mock import patch, MagicMock


def get_vnc_routes_module():
    """Get the routes/vnc module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.routes.vnc']


def get_codes_module():
    """Get the codes module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.codes']


@pytest.fixture
def app():
    """Flask app fixture."""
    from application import app as flask_app, api
    flask_app.config['TESTING'] = True
    if 'api' not in flask_app.blueprints:
        flask_app.register_blueprint(api, url_prefix='/api')
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


class TestStartVnc:
    """Tests for /api/vnc endpoint."""

    def test_start_vnc_success(self, client):
        """POST /api/vnc creates VNC session successfully."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create, \
             patch.object(vnc_routes, 'profiles') as mock_profiles:

            mock_vnc = MagicMock()
            mock_vnc.supports_load_check.return_value = False  # Skip load check
            mock_vnc.is_ecf.return_value = False
            mock_vnc.check_5900_open.return_value = False
            mock_vnc.launch_vnc.return_value = (True, 5901)
            mock_vnc.create_tunnel.return_value = 29001
            mock_create.return_value = (mock_vnc, '')

            mock_profiles.get_session_vnc_credentials.return_value = (True, {'password': 'test'})

            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session', 'loadCheck': True, 'loadCredentials': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            data = response.data
            # Should contain DONE marker
            assert codes.ICtrlStep.VNC.DONE in data

    def test_start_vnc_connection_failed(self, client):
        """POST /api/vnc returns error on connection failure."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_create.return_value = (mock_vnc, b'connection error')

            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert b'connection error' in response.data

    def test_start_vnc_overloaded(self, client):
        """POST /api/vnc returns overload error when server is loaded."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_vnc.supports_load_check.return_value = True  # Enable load check
            mock_vnc.is_load_high.return_value = True
            mock_create.return_value = (mock_vnc, '')

            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session', 'loadCheck': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            data = response.data
            assert codes.ICtrlError.SSH.OVER_LOADED in data

    def test_start_vnc_ecf_server(self, client):
        """POST /api/vnc handles ECF server (port 1000)."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_vnc.supports_load_check.return_value = False  # Skip load check
            mock_vnc.is_ecf.return_value = True  # ECF server
            mock_vnc.create_tunnel.return_value = 29001
            mock_create.return_value = (mock_vnc, '')

            # For ECF, credentials handling is skipped entirely (is_ecf() returns True)
            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Should contain DONE marker
            assert codes.ICtrlStep.VNC.DONE in response.data
            # Should not call launch_vnc for ECF
            mock_vnc.launch_vnc.assert_not_called()
            # Should create tunnel with port 1000
            mock_vnc.create_tunnel.assert_called_once_with(1000)

    def test_start_vnc_use_5900(self, client):
        """POST /api/vnc uses port 5900 when available."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create, \
             patch.object(vnc_routes, 'profiles') as mock_profiles:

            mock_vnc = MagicMock()
            mock_vnc.supports_load_check.return_value = False  # Skip load check
            mock_vnc.is_ecf.return_value = False
            mock_vnc.check_5900_open.return_value = True  # 5900 is open
            mock_vnc.get_vnc_password.return_value = (False, '')  # No password but 5900 is open
            mock_vnc.create_tunnel.return_value = 29001
            mock_create.return_value = (mock_vnc, '')

            mock_profiles.get_session_vnc_credentials.return_value = (False, '')

            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session', 'loadCredentials': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Should contain DONE marker
            assert codes.ICtrlStep.VNC.DONE in response.data
            # Should not call launch_vnc when using 5900
            mock_vnc.launch_vnc.assert_not_called()
            # Should create tunnel with port 5900
            mock_vnc.create_tunnel.assert_called_once_with(5900)

    def test_start_vnc_passwd_missing(self, client):
        """POST /api/vnc returns error when password is missing."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create, \
             patch.object(vnc_routes, 'profiles') as mock_profiles:

            mock_vnc = MagicMock()
            mock_vnc.supports_load_check.return_value = False  # Skip load check
            mock_vnc.is_ecf.return_value = False
            mock_vnc.check_5900_open.return_value = False
            mock_vnc.get_vnc_password.return_value = (False, '')
            mock_create.return_value = (mock_vnc, '')

            mock_profiles.get_session_vnc_credentials.return_value = (False, '')

            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session', 'loadCredentials': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            data = response.data
            assert codes.ICtrlError.VNC.PASSWD_MISSING in data

    def test_start_vnc_launch_failed(self, client):
        """POST /api/vnc returns error when VNC launch fails."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create, \
             patch.object(vnc_routes, 'profiles') as mock_profiles:

            mock_vnc = MagicMock()
            mock_vnc.supports_load_check.return_value = False  # Skip load check
            mock_vnc.is_ecf.return_value = False
            mock_vnc.check_5900_open.return_value = False
            mock_vnc.get_vnc_password.return_value = (True, 'password')
            mock_vnc.launch_vnc.return_value = (False, 'Quota exceeded')
            mock_create.return_value = (mock_vnc, '')

            mock_profiles.get_session_vnc_credentials.return_value = (False, '')

            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session', 'loadCredentials': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            data = response.data
            assert codes.ICtrlError.VNC.QUOTA_EXCEEDED in data

    def test_start_vnc_no_load_credentials(self, client):
        """POST /api/vnc clears credentials when loadCredentials=False."""
        vnc_routes = get_vnc_routes_module()
        codes = get_codes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create, \
             patch.object(vnc_routes, 'profiles') as mock_profiles:

            mock_vnc = MagicMock()
            mock_vnc.supports_load_check.return_value = False  # Skip load check
            mock_vnc.is_ecf.return_value = False
            mock_vnc.check_5900_open.return_value = False
            mock_vnc.launch_vnc.return_value = (True, 5901)
            mock_vnc.create_tunnel.return_value = 29001
            mock_create.return_value = (mock_vnc, '')

            response = client.post(
                '/api/vnc',
                json={'sessionID': 'test-session', 'loadCredentials': False},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Should contain DONE marker
            assert codes.ICtrlStep.VNC.DONE in response.data
            # Should have cleared credentials
            mock_profiles.set_session_vnc_credentials.assert_called_once_with('test-session', None)


class TestChangeVncpasswd:
    """Tests for /api/vncpasswd endpoint."""

    def test_change_vncpasswd_success(self, client):
        """POST /api/vncpasswd changes password successfully."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_vnc.reset_vnc_password.return_value = (True, '')
            mock_create.return_value = (mock_vnc, '')

            response = client.post(
                '/api/vncpasswd',
                json={'session_id': 'test-session', 'passwd': 'newpassword'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'
            mock_vnc.reset_vnc_password.assert_called_once_with('newpassword')

    def test_change_vncpasswd_connection_failed(self, client):
        """POST /api/vncpasswd returns 403 on connection failure."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_create.return_value = (mock_vnc, b'connection error')

            response = client.post(
                '/api/vncpasswd',
                json={'session_id': 'test-session', 'passwd': 'newpassword'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403

    def test_change_vncpasswd_reset_failed(self, client):
        """POST /api/vncpasswd returns 403 if reset fails."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_vnc.reset_vnc_password.return_value = (False, 'Reset failed')
            mock_create.return_value = (mock_vnc, '')

            response = client.post(
                '/api/vncpasswd',
                json={'session_id': 'test-session', 'passwd': 'newpassword'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403


class TestResetVnc:
    """Tests for /api/vnc_reset endpoint."""

    def test_reset_vnc_success(self, client):
        """POST /api/vnc_reset removes VNC settings successfully."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_vnc.remove_vnc_settings.return_value = (True, '')
            mock_create.return_value = (mock_vnc, '')

            response = client.post(
                '/api/vnc_reset',
                json={'session_id': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_reset_vnc_connection_failed(self, client):
        """POST /api/vnc_reset returns 403 on connection failure."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_create.return_value = (mock_vnc, b'connection error')

            response = client.post(
                '/api/vnc_reset',
                json={'session_id': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403

    def test_reset_vnc_failed(self, client):
        """POST /api/vnc_reset returns 403 if removal fails."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'create_connection') as mock_create:
            mock_vnc = MagicMock()
            mock_vnc.remove_vnc_settings.return_value = (False, 'Removal failed')
            mock_create.return_value = (mock_vnc, '')

            response = client.post(
                '/api/vnc_reset',
                json={'session_id': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403


class TestVncCredentials:
    """Tests for /api/vnc_credentials endpoint."""

    def test_vnc_credentials_success(self, client):
        """PUT /api/vnc_credentials saves credentials successfully."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'profiles') as mock_profiles:
            mock_profiles.set_session_vnc_credentials.return_value = (True, '')

            response = client.put(
                '/api/vnc_credentials',
                json={'session_id': 'test-session', 'credentials': {'password': 'test'}},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_vnc_credentials_failed(self, client):
        """PUT /api/vnc_credentials returns 403 on failure."""
        vnc_routes = get_vnc_routes_module()

        with patch.object(vnc_routes, 'profiles') as mock_profiles:
            mock_profiles.set_session_vnc_credentials.return_value = (False, 'Session not found')

            response = client.put(
                '/api/vnc_credentials',
                json={'session_id': 'nonexistent', 'credentials': {'password': 'test'}},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
