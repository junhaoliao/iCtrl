"""
Integration tests for Profile/DBProfile.py.

These tests require the PostgreSQL Docker container to be running.
Run with: docker compose -f docker-compose.test.yml up -d postgres
"""

import os
import sys
import pytest
import requests
import uuid

# Test against the running ictrl-server-be container which has DBProfile
BASE_URL = os.environ.get('ICTRL_TEST_DB_URL', 'https://localhost:25001')

# Disable SSL verification warnings for self-signed certs
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def is_db_mode_available():
    """Check if the DB mode server is available."""
    try:
        response = requests.get(f'{BASE_URL}/api/logout', timeout=5, verify=False)
        # In DB mode, this should return 200 and 'logged out'
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False


pytestmark = pytest.mark.skipif(
    not is_db_mode_available(),
    reason="DB mode server not available (run docker compose -f docker-compose.test.yml up -d)"
)


class TestDBProfileUserManagement:
    """Integration tests for user management in DBProfile mode."""

    @pytest.fixture
    def unique_user(self):
        """Generate unique user credentials for each test."""
        unique_id = str(uuid.uuid4())[:8]
        return {
            'username': f'testuser_{unique_id}',
            'password': 'TestPass123!',
            'email': f'testuser_{unique_id}@mail.utoronto.ca'
        }

    def test_register_user_success(self, unique_user):
        """Test user registration in DB mode."""
        response = requests.post(
            f'{BASE_URL}/api/register',
            json=unique_user,
            verify=False
        )
        assert response.status_code == 200
        assert b'Registration Successful' in response.content

    def test_register_user_duplicate_username(self, unique_user):
        """Test that duplicate usernames are rejected."""
        # First registration
        requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)

        # Try to register same username with different email
        duplicate = unique_user.copy()
        duplicate['email'] = f'other_{unique_user["username"]}@mail.utoronto.ca'

        response = requests.post(f'{BASE_URL}/api/register', json=duplicate, verify=False)
        assert response.status_code == 422
        assert b'ACCOUNT_DUPLICATE_USERNAME' in response.content

    def test_register_user_duplicate_email(self, unique_user):
        """Test that duplicate emails are rejected."""
        # First registration
        requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)

        # Try to register same email with different username
        duplicate = unique_user.copy()
        duplicate['username'] = f'other_{unique_user["username"]}'

        response = requests.post(f'{BASE_URL}/api/register', json=duplicate, verify=False)
        assert response.status_code == 422
        assert b'ACCOUNT_DUPLICATE_EMAIL' in response.content

    def test_register_user_invalid_email(self, unique_user):
        """Test that invalid emails are rejected."""
        unique_user['email'] = 'invalid@gmail.com'  # Not utoronto.ca

        response = requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)
        assert response.status_code == 422

    def test_register_user_weak_password(self, unique_user):
        """Test that weak passwords are rejected."""
        unique_user['password'] = 'weak'

        response = requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)
        assert response.status_code == 422

    def test_login_wrong_username(self):
        """Test login fails with wrong username."""
        response = requests.post(
            f'{BASE_URL}/api/login',
            json={'username': 'nonexistent_user_xyz', 'password': 'TestPass123!'},
            verify=False
        )
        assert response.status_code == 403
        assert b'ACCOUNT_WRONG_USERNAME' in response.content

    def test_login_not_activated(self, unique_user):
        """Test login fails for non-activated account."""
        # Register but don't activate
        requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)

        # Try to login
        response = requests.post(
            f'{BASE_URL}/api/login',
            json={'username': unique_user['username'], 'password': unique_user['password']},
            verify=False
        )
        assert response.status_code == 401
        assert b'ACCOUNT_NOT_ACTIVATED' in response.content

    def test_resend_activation_success(self, unique_user):
        """Test resend activation email."""
        # Register first
        requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)

        # Wait for cooldown (2 seconds in test mode)
        import time
        time.sleep(3)

        # Resend activation
        response = requests.post(
            f'{BASE_URL}/api/resend_activation',
            json={'username': unique_user['username']},
            verify=False
        )
        assert response.status_code == 200
        assert b'sent' in response.content

    def test_resend_activation_cooldown(self, unique_user):
        """Test resend activation respects cooldown."""
        # Register first
        requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)

        # Try to resend immediately (within cooldown)
        response = requests.post(
            f'{BASE_URL}/api/resend_activation',
            json={'username': unique_user['username']},
            verify=False
        )
        assert response.status_code == 429  # Too Many Requests

    def test_activate_user_wrong_code(self, unique_user):
        """Test activation fails with wrong code."""
        # Register first
        requests.post(f'{BASE_URL}/api/register', json=unique_user, verify=False)

        # Try to activate with wrong code
        response = requests.get(
            f'{BASE_URL}/api/activate',
            params={'userid': '99999', 'code': 'wrong-code'},
            verify=False
        )
        assert response.status_code == 200
        assert b'Failed to activate' in response.content

    def test_logout(self, unique_user):
        """Test logout endpoint."""
        response = requests.get(f'{BASE_URL}/api/logout', verify=False)
        assert response.status_code == 200
        assert b'logged out' in response.content


class TestDBProfileProfileEndpoints:
    """Integration tests for profile endpoints in DBProfile mode."""

    def test_profiles_without_login(self):
        """Test /api/profiles returns 403 when not logged in."""
        response = requests.get(f'{BASE_URL}/api/profiles', verify=False)
        # Should return 403 because user is not logged in
        assert response.status_code == 403

    def test_userid_without_login(self):
        """Test /api/userid returns 403 when not logged in."""
        response = requests.get(f'{BASE_URL}/api/userid', verify=False)
        # Should return 403 because user is not logged in
        assert response.status_code == 403
