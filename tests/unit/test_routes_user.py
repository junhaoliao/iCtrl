"""
Unit tests for routes/user.py.

Tests the user route handlers.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock


def get_user_routes_module():
    """Get the routes/user module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.routes.user']


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


class TestUserID:
    """Tests for /api/userid endpoint."""

    def test_userid_success(self, client):
        """GET /api/userid returns user id."""
        user_routes = get_user_routes_module()

        mock_user = MagicMock()
        mock_user.id = 12345

        with patch.object(user_routes, 'profiles') as mock_profiles:
            mock_profiles.get_user.return_value = mock_user

            response = client.get(
                '/api/userid',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'12345'

    def test_userid_zero_for_local_profile(self, client):
        """GET /api/userid returns 0 for local profile."""
        user_routes = get_user_routes_module()

        mock_user = MagicMock()
        mock_user.id = 0

        with patch.object(user_routes, 'profiles') as mock_profiles:
            mock_profiles.get_user.return_value = mock_user

            response = client.get(
                '/api/userid',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'0'


class TestRegister:
    """Tests for /api/register endpoint."""

    def test_register_post_success(self, client):
        """POST /api/register creates user successfully."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/register',
                json={
                    'username': 'testuser',
                    'password': 'testpass',
                    'email': 'test@example.com'
                },
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'Registration Successful'
            mock_profiles.add_user.assert_called_once_with('testuser', 'testpass', 'test@example.com')

    def test_register_get_success(self, client):
        """GET /api/register creates user successfully."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.get(
                '/api/register?username=testuser&password=testpass&email=test@example.com',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'Registration Successful'
            mock_profiles.add_user.assert_called_once_with('testuser', 'testpass', 'test@example.com')

    def test_register_post_missing_username(self, client):
        """POST /api/register returns 403 when username missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/register',
                json={
                    'password': 'testpass',
                    'email': 'test@example.com'
                },
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.add_user.assert_not_called()

    def test_register_post_missing_password(self, client):
        """POST /api/register returns 403 when password missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/register',
                json={
                    'username': 'testuser',
                    'email': 'test@example.com'
                },
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.add_user.assert_not_called()

    def test_register_post_missing_email(self, client):
        """POST /api/register returns 403 when email missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/register',
                json={
                    'username': 'testuser',
                    'password': 'testpass'
                },
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.add_user.assert_not_called()

    def test_register_get_missing_param(self, client):
        """GET /api/register returns 403 when parameter missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.get(
                '/api/register?username=testuser&password=testpass',  # missing email
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.add_user.assert_not_called()


class TestLogin:
    """Tests for /api/login endpoint."""

    def test_login_post_success(self, client):
        """POST /api/login logs in user successfully."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/login',
                json={
                    'username': 'testuser',
                    'password': 'testpass'
                },
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'logged in'
            mock_profiles.login.assert_called_once_with('testuser', 'testpass')

    def test_login_get_success(self, client):
        """GET /api/login logs in user successfully."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.get(
                '/api/login?username=testuser&password=testpass',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'logged in'
            mock_profiles.login.assert_called_once_with('testuser', 'testpass')

    def test_login_post_missing_username(self, client):
        """POST /api/login returns 403 when username missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/login',
                json={
                    'password': 'testpass'
                },
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.login.assert_not_called()

    def test_login_post_missing_password(self, client):
        """POST /api/login returns 403 when password missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/login',
                json={
                    'username': 'testuser'
                },
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.login.assert_not_called()

    def test_login_get_missing_param(self, client):
        """GET /api/login returns 403 when parameter missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.get(
                '/api/login?username=testuser',  # missing password
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.login.assert_not_called()


class TestLogout:
    """Tests for /api/logout endpoint."""

    def test_logout_success(self, client):
        """GET /api/logout logs out user successfully."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.get(
                '/api/logout',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'logged out'
            mock_profiles.logout.assert_called_once()


class TestResendActivation:
    """Tests for /api/resend_activation endpoint."""

    def test_resend_activation_success(self, client):
        """POST /api/resend_activation sends activation email."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/resend_activation',
                json={'username': 'testuser'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'sent'
            mock_profiles.send_activation_email.assert_called_once_with('testuser')

    def test_resend_activation_missing_username(self, client):
        """POST /api/resend_activation returns 403 when username missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.post(
                '/api/resend_activation',
                json={},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.send_activation_email.assert_not_called()


class TestActivate:
    """Tests for /api/activate endpoint."""

    def test_activate_success(self, client):
        """GET /api/activate activates user account."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            mock_profiles.activate_user.return_value = True

            response = client.get(
                '/api/activate?userid=123&code=abc123',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert b'Your account has been activated' in response.data
            mock_profiles.activate_user.assert_called_once_with('123', 'abc123')

    def test_activate_failed(self, client):
        """GET /api/activate returns failure message when activation fails."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            mock_profiles.activate_user.return_value = False

            response = client.get(
                '/api/activate?userid=123&code=wrongcode',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert b'Failed to activate' in response.data

    def test_activate_missing_userid(self, client):
        """GET /api/activate returns 403 when userid missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.get(
                '/api/activate?code=abc123',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.activate_user.assert_not_called()

    def test_activate_missing_code(self, client):
        """GET /api/activate returns 403 when code missing."""
        user_routes = get_user_routes_module()

        with patch.object(user_routes, 'profiles') as mock_profiles:
            response = client.get(
                '/api/activate?userid=123',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
            mock_profiles.activate_user.assert_not_called()
