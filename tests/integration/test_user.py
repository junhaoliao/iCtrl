"""
Integration tests for user routes (routes/user.py)

Tests for: /userid, /register, /login, /logout, /resend_activation, /activate
"""

import pytest
import time
from tests.conftest import ICtrlClient, TestConfig, get_emails
from tests.helpers import assert_success_response, assert_error_response


# =============================================================================
# Local Mode Tests
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
class TestUserIdLocalMode:
    """Tests for /userid endpoint in local mode."""

    def test_get_userid_returns_zero(self, local_client: ICtrlClient):
        """Local mode always returns user ID 0."""
        resp = local_client.get("/api/userid")
        assert resp.status_code == 200
        assert resp.text == "0"

    def test_userid_without_auth_fails(self, config: TestConfig, ensure_ictrl_local):
        """Request without auth key should fail."""
        client = ICtrlClient(config.ictrl_local_url, auth_key=None)
        resp = client.get("/api/userid")
        assert resp.status_code == 403

    def test_userid_with_wrong_auth_key_fails(self, config: TestConfig, ensure_ictrl_local):
        """Request with wrong auth key should fail (exercises line 110-111 in utils.py)."""
        client = ICtrlClient(config.ictrl_local_url, auth_key="wrong-auth-key")
        resp = client.get("/api/userid")
        assert resp.status_code == 403
        assert "not authorized" in resp.text

    def test_userid_with_wrong_auth_type_fails(self, config: TestConfig, ensure_ictrl_local):
        """Request with wrong auth type (Basic instead of Bearer) should fail."""
        import requests
        # Manually set Basic auth instead of Bearer
        resp = requests.get(
            f"{config.ictrl_local_url}/api/userid",
            headers={"Authorization": f"Basic {config.ictrl_local_auth_key}"},
            verify=False
        )
        assert resp.status_code == 403
        assert "not authorized" in resp.text


# =============================================================================
# Database Mode Tests
# =============================================================================

@pytest.mark.integration
@pytest.mark.db_mode
class TestRegisterDBMode:
    """Tests for /register endpoint in database mode."""

    def test_register_success(
        self,
        db_client: ICtrlClient,
        clean_db,
        clear_mailbox,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Successful registration with valid credentials."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })
        assert resp.status_code == 200
        assert "Registration Successful" in resp.text

    def test_register_missing_username(
        self,
        db_client: ICtrlClient,
        clean_db,
        valid_password: str,
        valid_email: str
    ):
        """Registration without username should fail."""
        resp = db_client.post("/api/register", json={
            "password": valid_password,
            "email": valid_email
        })
        assert resp.status_code == 403
        assert "username" in resp.text.lower()

    def test_register_missing_password(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_email: str
    ):
        """Registration without password should fail."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "email": valid_email
        })
        assert resp.status_code == 403
        assert "password" in resp.text.lower()

    def test_register_missing_email(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_password: str
    ):
        """Registration without email should fail."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password
        })
        assert resp.status_code == 403
        assert "email" in resp.text.lower()

    def test_register_invalid_password_too_short(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_email: str
    ):
        """Password validation: too short."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": "Ab1!",
            "email": valid_email
        })
        assert resp.status_code == 422

    def test_register_invalid_password_no_digit(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_email: str
    ):
        """Password validation: missing digit."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": "TestPass!",
            "email": valid_email
        })
        assert resp.status_code == 422

    def test_register_invalid_password_too_long(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_email: str
    ):
        """Password validation: exceeds 32 characters."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": "A" * 30 + "b1!",  # 33 chars
            "email": valid_email
        })
        assert resp.status_code == 422
        assert "exceed 32" in resp.text

    def test_register_invalid_password_no_uppercase(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_email: str
    ):
        """Password validation: missing uppercase letter."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": "testpass1!",
            "email": valid_email
        })
        assert resp.status_code == 422
        assert "uppercase" in resp.text

    def test_register_invalid_password_no_lowercase(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_email: str
    ):
        """Password validation: missing lowercase letter."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": "TESTPASS1!",
            "email": valid_email
        })
        assert resp.status_code == 422
        assert "lowercase" in resp.text

    def test_register_invalid_password_no_special(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_email: str
    ):
        """Password validation: missing special symbol."""
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": "TestPass1",
            "email": valid_email
        })
        assert resp.status_code == 422
        assert "symbol" in resp.text

    def test_register_duplicate_username(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Duplicate username should fail."""
        # First registration
        db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })

        # Second registration with same username
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": f"other_{valid_email}"
        })
        assert resp.status_code == 422
        assert "ACCOUNT_DUPLICATE_USERNAME" in resp.text

    def test_register_duplicate_email(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Duplicate email should fail."""
        # First registration
        db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })

        # Second registration with same email
        resp = db_client.post("/api/register", json={
            "username": f"other_{unique_username}",
            "password": valid_password,
            "email": valid_email
        })
        assert resp.status_code == 422
        assert "ACCOUNT_DUPLICATE_EMAIL" in resp.text

    def test_register_sends_activation_email(
        self,
        db_client: ICtrlClient,
        config: TestConfig,
        clean_db,
        clear_mailbox,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Registration should send activation email."""
        db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })

        # Wait for email
        time.sleep(2)
        emails = get_emails(config)

        assert len(emails) >= 1
        # Check the email was sent to the right address
        # Mailpit API: To is a list of {"Name": "", "Address": "email@example.com"}
        last_email = emails[-1]
        recipients = [r.get("Address", "") for r in last_email.get("To", [])]
        assert valid_email in recipients


@pytest.mark.integration
@pytest.mark.db_mode
class TestLoginDBMode:
    """Tests for /login endpoint in database mode."""

    @pytest.fixture
    def registered_user(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Create a registered (but not activated) user."""
        db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })
        return {"username": unique_username, "password": valid_password}

    @pytest.fixture
    def activated_user(
        self,
        db_client: ICtrlClient,
        config: TestConfig,
        clean_db,
        clear_mailbox,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Create a registered AND activated user."""
        import re

        # Register
        db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })

        # Wait for activation email
        time.sleep(2)
        emails = get_emails(config)

        # Find the activation email and extract the code
        for email in reversed(emails):
            recipients = [r.get("Address", "") for r in email.get("To", [])]
            if valid_email in recipients:
                # Get the email HTML content from Mailpit
                msg_id = email.get("ID")
                import requests
                resp = requests.get(f"http://{config.mail_smtp_host}:{config.mail_web_port}/api/v1/message/{msg_id}")
                msg_data = resp.json()
                html_body = msg_data.get("HTML", "")

                # Extract userid and code from activation link
                # Link format: /api/activate?userid=XXX&code=YYY
                # Note: & may appear as &amp; in HTML or as plain &
                match = re.search(r'userid=(\d+)(?:&amp;|&)code=([a-f0-9-]+)', html_body)
                if match:
                    userid = match.group(1)
                    code = match.group(2)

                    # Activate the account
                    db_client.get("/api/activate", params={
                        "userid": userid,
                        "code": code
                    })
                    break

        return {"username": unique_username, "password": valid_password, "email": valid_email}

    def test_login_success(
        self,
        db_client: ICtrlClient,
        activated_user: dict
    ):
        """Login with activated account should succeed."""
        resp = db_client.post("/api/login", json={
            "username": activated_user["username"],
            "password": activated_user["password"]
        })
        assert resp.status_code == 200
        assert "logged in" in resp.text

    def test_login_wrong_password(
        self,
        db_client: ICtrlClient,
        activated_user: dict
    ):
        """Login with wrong password should fail."""
        resp = db_client.post("/api/login", json={
            "username": activated_user["username"],
            "password": "WrongPass123!"
        })
        assert resp.status_code == 403
        assert "ACCOUNT_WRONG_PASSWORD" in resp.text

    def test_login_not_activated(
        self,
        db_client: ICtrlClient,
        registered_user: dict
    ):
        """Login to non-activated account should fail."""
        resp = db_client.post("/api/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        assert resp.status_code == 401
        assert "ACCOUNT_NOT_ACTIVATED" in resp.text

    def test_login_wrong_username(
        self,
        db_client: ICtrlClient,
        clean_db
    ):
        """Login with non-existent username should fail."""
        resp = db_client.post("/api/login", json={
            "username": "nonexistent_user",
            "password": "SomePass1!"
        })
        assert resp.status_code == 403
        assert "ACCOUNT_WRONG_USERNAME" in resp.text

    def test_login_missing_username(self, db_client: ICtrlClient, clean_db):
        """Login without username should fail."""
        resp = db_client.post("/api/login", json={
            "password": "SomePass1!"
        })
        assert resp.status_code == 403

    def test_login_missing_password(
        self,
        db_client: ICtrlClient,
        clean_db,
        unique_username: str
    ):
        """Login without password should fail."""
        resp = db_client.post("/api/login", json={
            "username": unique_username
        })
        assert resp.status_code == 403


@pytest.mark.integration
@pytest.mark.db_mode
class TestLogoutDBMode:
    """Tests for /logout endpoint in database mode."""

    def test_logout_returns_success(self, db_client: ICtrlClient):
        """Logout should return success message."""
        resp = db_client.get("/api/logout")
        assert resp.status_code == 200
        assert "logged out" in resp.text


@pytest.mark.integration
@pytest.mark.db_mode
class TestResendActivationDBMode:
    """Tests for /resend_activation endpoint in database mode."""

    @pytest.fixture
    def registered_user(
        self,
        db_client: ICtrlClient,
        clean_db,
        clear_mailbox,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Create a registered (but not activated) user."""
        db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })
        # Wait for initial email
        time.sleep(1)
        return {"username": unique_username, "password": valid_password}

    def test_resend_activation_success(
        self,
        db_client: ICtrlClient,
        config: TestConfig,
        clear_mailbox,
        registered_user: dict
    ):
        """Resend activation email should work."""
        # Wait for cooldown from registration email
        # The cooldown is configured via ICTRL_RESEND_COOLDOWN_SEC (default 30s, 2s in tests)
        time.sleep(3)

        resp = db_client.post("/api/resend_activation", json={
            "username": registered_user["username"]
        })
        assert resp.status_code == 200
        assert resp.text == "sent"

    def test_resend_activation_rate_limited(
        self,
        db_client: ICtrlClient,
        registered_user: dict
    ):
        """Resend should be rate limited (30 seconds)."""
        # First resend
        db_client.post("/api/resend_activation", json={
            "username": registered_user["username"]
        })

        # Immediate second resend should fail
        resp = db_client.post("/api/resend_activation", json={
            "username": registered_user["username"]
        })
        assert resp.status_code == 429

    def test_resend_activation_missing_username(self, db_client: ICtrlClient, clean_db):
        """Resend without username should fail."""
        resp = db_client.post("/api/resend_activation", json={})
        assert resp.status_code == 403

    def test_resend_activation_nonexistent_user(self, db_client: ICtrlClient, clean_db):
        """Resend for non-existent user should fail."""
        resp = db_client.post("/api/resend_activation", json={
            "username": "nonexistent_user_12345"
        })
        assert resp.status_code == 403


@pytest.mark.integration
@pytest.mark.db_mode
class TestActivateDBMode:
    """Tests for /activate endpoint in database mode."""

    def test_activate_invalid_code(self, db_client: ICtrlClient, clean_db):
        """Activation with invalid code should fail."""
        resp = db_client.get("/api/activate", params={
            "userid": "999",
            "code": "invalid-code-12345"
        })
        assert resp.status_code == 200  # Returns HTML, not error status
        assert "Failed to activate" in resp.text

    def test_activate_missing_userid(self, db_client: ICtrlClient, clean_db):
        """Activation without userid should fail."""
        resp = db_client.get("/api/activate", params={
            "code": "some-code"
        })
        assert resp.status_code == 403

    def test_activate_missing_code(self, db_client: ICtrlClient, clean_db):
        """Activation without code should fail."""
        resp = db_client.get("/api/activate", params={
            "userid": "1"
        })
        assert resp.status_code == 403


@pytest.mark.integration
@pytest.mark.db_mode
class TestUserIdDBMode:
    """Tests for /userid endpoint in database mode."""

    def test_userid_not_logged_in(self, db_client: ICtrlClient, clean_db):
        """User ID request without login should fail."""
        resp = db_client.get("/api/userid")
        assert resp.status_code == 403
        assert "not logged in" in resp.text.lower()
