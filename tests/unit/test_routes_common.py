"""
Unit tests for routes/common.py.

Tests the common route handlers and create_connection helper.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock
from werkzeug.exceptions import HTTPException


def get_flask_app():
    """Get the Flask app from sys.modules (already loaded by conftest)."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application'].app


def get_common_module():
    """Get the routes/common module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.routes.common']


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
    # Register blueprint if not already registered
    if 'api' not in flask_app.blueprints:
        flask_app.register_blueprint(api, url_prefix='/api')
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


class TestCreateConnection:
    """Tests for create_connection helper function."""

    def test_create_connection_session_not_found(self, app):
        """create_connection aborts with 403 if session doesn't exist."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles:
                mock_profiles.get_session_info.return_value = (None, None, None, None, None)

                with pytest.raises(HTTPException) as exc_info:
                    common.create_connection("nonexistent-id", codes.ConnectionType.GENERAL)

                assert exc_info.value.code == 403
                assert "does not exist" in str(exc_info.value.description)

    def test_create_connection_general_type(self, app):
        """create_connection creates Connection for GENERAL type."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Connection') as MockConnection:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, "nickname"
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (True, '')
                MockConnection.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.GENERAL)

                MockConnection.assert_called_once()
                mock_conn.connect.assert_called_once_with(
                    "test.host.com", "testuser",
                    key_filename="/path/to/key", private_key_str=None
                )
                assert reason == ''

    def test_create_connection_vnc_type(self, app):
        """create_connection creates VNC for VNC type."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'VNC') as MockVNC:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (True, '')
                MockVNC.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.VNC)

                MockVNC.assert_called_once()

    def test_create_connection_term_type(self, app):
        """create_connection creates Term for TERM type."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Term') as MockTerm:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (True, '')
                MockTerm.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.TERM)

                MockTerm.assert_called_once()

    def test_create_connection_sftp_type(self, app):
        """create_connection creates SFTP for SFTP type."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'SFTP') as MockSFTP:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (True, '')
                MockSFTP.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.SFTP)

                MockSFTP.assert_called_once()

    def test_create_connection_audio_type(self, app):
        """create_connection creates Audio for AUDIO type."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Audio') as MockAudio:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (True, '')
                MockAudio.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.AUDIO)

                MockAudio.assert_called_once()

    def test_create_connection_invalid_type(self, app):
        """create_connection raises TypeError for invalid type."""
        common = get_common_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles:
                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )

                with pytest.raises(TypeError) as exc_info:
                    common.create_connection("test-session", 999)

                assert "Invalid type" in str(exc_info.value)

    def test_create_connection_host_unreachable_errno60(self, app):
        """create_connection returns HOST_UNREACHABLE for Errno 60."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Connection') as MockConnection:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (False, '[Errno 60] Connection timed out')
                MockConnection.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.GENERAL)

                # reason should be the ICtrlError.SSH.HOST_UNREACHABLE as bytes
                assert isinstance(reason, bytes)
                assert reason == common.int_to_bytes(codes.ICtrlError.SSH.HOST_UNREACHABLE)

    def test_create_connection_host_unreachable_errno64(self, app):
        """create_connection returns HOST_UNREACHABLE for Errno 64."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Connection') as MockConnection:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (False, '[Errno 64] Host is down')
                MockConnection.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.GENERAL)

                assert isinstance(reason, bytes)

    def test_create_connection_host_unreachable_errno51(self, app):
        """create_connection returns HOST_UNREACHABLE for Errno 51."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Connection') as MockConnection:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (False, '[Errno 51] Network is unreachable')
                MockConnection.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.GENERAL)

                assert isinstance(reason, bytes)

    def test_create_connection_host_unreachable_timeout(self, app):
        """create_connection returns HOST_UNREACHABLE for timeout."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Connection') as MockConnection:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (False, 'timed out')
                MockConnection.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.GENERAL)

                assert isinstance(reason, bytes)

    def test_create_connection_auth_wrong(self, app):
        """create_connection returns AUTH_WRONG for RSA key error."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Connection') as MockConnection:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (False, 'encountered RSA key, expected OPENSSH key')
                MockConnection.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.GENERAL)

                assert isinstance(reason, bytes)
                assert reason == common.int_to_bytes(codes.ICtrlError.SSH.AUTH_WRONG)

    def test_create_connection_general_error(self, app):
        """create_connection returns GENERAL error for unknown errors."""
        common = get_common_module()
        codes = get_codes_module()

        with app.app_context():
            with patch.object(common, 'profiles') as mock_profiles, \
                 patch.object(common, 'Connection') as MockConnection:

                mock_profiles.get_session_info.return_value = (
                    "test.host.com", "testuser", "/path/to/key", None, None
                )
                mock_conn = MagicMock()
                mock_conn.connect.return_value = (False, 'Some unknown error')
                MockConnection.return_value = mock_conn

                conn, reason = common.create_connection("test-session", codes.ConnectionType.GENERAL)

                assert isinstance(reason, bytes)
                assert reason == common.int_to_bytes(codes.ICtrlError.SSH.GENERAL)


class TestGetProfiles:
    """Tests for /api/profiles endpoint."""

    def test_get_profiles_success(self, client):
        """GET /api/profiles returns profile data."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles:
            mock_profiles.query.return_value = {
                "version": 1,
                "sessions": {
                    "session1": {"host": "host1.com", "username": "user1"}
                }
            }

            response = client.get('/api/profiles', headers={"Authorization": "Bearer test-auth-key"})

            assert response.status_code == 200
            data = response.get_json()
            assert "sessions" in data
            assert "session1" in data["sessions"]


class TestHandleSession:
    """Tests for /api/session endpoint."""

    def test_get_session_info(self, client):
        """GET /api/session returns session info."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles:
            mock_profiles.get_session_info.return_value = (
                "test.host.com", "testuser", "/path", None, "MyServer"
            )

            response = client.get(
                '/api/session?id=test-session',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data["host"] == "test.host.com"
            assert data["username"] == "testuser"
            assert data["nickname"] == "MyServer"

    def test_post_session_success(self, client):
        """POST /api/session creates a new session."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles, \
             patch.object(common, 'Connection') as MockConnection:

            mock_conn = MagicMock()
            mock_conn.connect.return_value = (True, '')
            MockConnection.return_value = mock_conn
            mock_profiles.add_session.return_value = (True, '')

            response = client.post(
                '/api/session',
                json={"host": "test.host.com", "username": "testuser", "password": "testpass"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_post_session_connection_failed(self, client):
        """POST /api/session returns 403 if connection fails."""
        common = get_common_module()

        with patch.object(common, 'Connection') as MockConnection:
            mock_conn = MagicMock()
            mock_conn.connect.return_value = (False, 'Connection refused')
            MockConnection.return_value = mock_conn

            response = client.post(
                '/api/session',
                json={"host": "test.host.com", "username": "testuser", "password": "testpass"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403

    def test_post_session_add_failed(self, client):
        """POST /api/session returns 500 if adding session fails."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles, \
             patch.object(common, 'Connection') as MockConnection:

            mock_conn = MagicMock()
            mock_conn.connect.return_value = (True, '')
            MockConnection.return_value = mock_conn
            mock_profiles.add_session.return_value = (False, 'Database error')

            response = client.post(
                '/api/session',
                json={"host": "test.host.com", "username": "testuser", "password": "testpass"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 500

    def test_patch_session_nickname(self, client):
        """PATCH /api/session can update nickname."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles:
            mock_profiles.set_session_nickname.return_value = (True, '')

            response = client.patch(
                '/api/session',
                json={"session_id": "test-session", "nickname": "NewNick"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            mock_profiles.set_session_nickname.assert_called_once_with("test-session", "NewNick")

    def test_patch_session_nickname_failed(self, client):
        """PATCH /api/session returns 400 if nickname update fails."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles:
            mock_profiles.set_session_nickname.return_value = (False, 'Nickname too long')

            response = client.patch(
                '/api/session',
                json={"session_id": "test-session", "nickname": "TooLongNicknameValue"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 400

    def test_patch_session_change_host(self, client):
        """PATCH /api/session can change host."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles, \
             patch.object(common, 'create_connection') as mock_create_conn, \
             patch.object(common, 'threading') as mock_threading:

            # Original host is "oldhost.domain.com", domain extraction finds ".domain.com"
            mock_profiles.get_session_info.return_value = (
                "oldhost.domain.com", "testuser", "/path", None, None
            )
            mock_profiles.change_host.return_value = (True, '')
            mock_conn = MagicMock()
            mock_create_conn.return_value = (mock_conn, '')

            response = client.patch(
                '/api/session',
                json={"session_id": "test-session", "host": "newhost"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Host should be concatenated with domain
            mock_profiles.change_host.assert_called_once_with("test-session", "newhost.domain.com")

    def test_patch_session_change_host_with_domain(self, client):
        """PATCH /api/session can change host with explicit domain."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles, \
             patch.object(common, 'create_connection') as mock_create_conn, \
             patch.object(common, 'threading') as mock_threading:

            mock_profiles.change_host.return_value = (True, '')
            mock_conn = MagicMock()
            mock_create_conn.return_value = (mock_conn, '')

            response = client.patch(
                '/api/session',
                json={"session_id": "test-session", "host": "new", "domain": ".example.com"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            mock_profiles.change_host.assert_called_once_with("test-session", "new.example.com")

    def test_patch_session_change_host_failed(self, client):
        """PATCH /api/session returns 403 if host change fails."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles, \
             patch.object(common, 'create_connection') as mock_create_conn, \
             patch.object(common, 'threading') as mock_threading:

            mock_profiles.get_session_info.return_value = (
                "old.host.domain.com", "testuser", "/path", None, None
            )
            mock_profiles.change_host.return_value = (False, 'Session not found')
            mock_conn = MagicMock()
            mock_create_conn.return_value = (mock_conn, '')

            response = client.patch(
                '/api/session',
                json={"session_id": "test-session", "host": "new.host"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403

    def test_patch_session_no_existing_session(self, client):
        """PATCH /api/session returns 400 if session doesn't exist."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles, \
             patch.object(common, 'create_connection') as mock_create_conn, \
             patch.object(common, 'threading') as mock_threading:

            mock_profiles.get_session_info.return_value = (None, None, None, None, None)
            mock_create_conn.side_effect = HTTPException(description="Session not found")

            response = client.patch(
                '/api/session',
                json={"session_id": "nonexistent", "host": "new.host"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 400

    def test_delete_session_success(self, client):
        """DELETE /api/session deletes a session."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles:
            mock_profiles.delete_session.return_value = (True, '')

            response = client.delete(
                '/api/session?session_id=test-session',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_delete_session_failed(self, client):
        """DELETE /api/session returns 403 if deletion fails."""
        common = get_common_module()

        with patch.object(common, 'profiles') as mock_profiles:
            mock_profiles.delete_session.return_value = (False, 'Session not found')

            response = client.delete(
                '/api/session?session_id=nonexistent',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403


class TestExecBlocking:
    """Tests for /api/exec_blocking endpoint."""

    def test_exec_blocking_success(self, client):
        """POST /api/exec_blocking executes command and returns result."""
        common = get_common_module()
        codes = get_codes_module()

        with patch.object(common, 'create_connection') as mock_create_conn:
            mock_conn = MagicMock()
            mock_conn.exec_command_blocking.return_value = (True, 0, ['hello', 'world'], [])
            mock_create_conn.return_value = (mock_conn, '')

            response = client.post(
                '/api/exec_blocking',
                json={"session_id": "test-session", "cmd": "echo hello; echo world"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert b'hello' in response.data
            assert b'world' in response.data

    def test_exec_blocking_large_output(self, client):
        """POST /api/exec_blocking handles large output mode."""
        common = get_common_module()
        codes = get_codes_module()

        with patch.object(common, 'create_connection') as mock_create_conn:
            mock_conn = MagicMock()
            mock_conn.exec_command_blocking_large.return_value = 'large output data'
            mock_create_conn.return_value = (mock_conn, '')

            response = client.post(
                '/api/exec_blocking',
                json={"session_id": "test-session", "cmd": "cat large_file", "large": True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert b'large output data' in response.data

    def test_exec_blocking_connection_failed(self, client):
        """POST /api/exec_blocking returns 403 if connection fails."""
        common = get_common_module()
        codes = get_codes_module()

        with patch.object(common, 'create_connection') as mock_create_conn:
            mock_conn = MagicMock()
            mock_create_conn.return_value = (mock_conn, b'\x64')  # Non-empty reason (error code)

            response = client.post(
                '/api/exec_blocking',
                json={"session_id": "test-session", "cmd": "ls"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403

    def test_exec_blocking_command_failed(self, client):
        """POST /api/exec_blocking returns 500 if command execution fails."""
        common = get_common_module()
        codes = get_codes_module()

        with patch.object(common, 'create_connection') as mock_create_conn:
            mock_conn = MagicMock()
            mock_conn.exec_command_blocking.return_value = (False, 1, [], ['error'])
            mock_create_conn.return_value = (mock_conn, '')

            response = client.post(
                '/api/exec_blocking',
                json={"session_id": "test-session", "cmd": "invalid_command"},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 500
