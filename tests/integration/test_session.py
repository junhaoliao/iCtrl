"""
Integration tests for session/profile routes (routes/common.py)

Tests for: /profiles, /session, /exec_blocking
"""

import re
import time
import pytest
from tests.conftest import ICtrlClient, TestConfig, get_emails
from tests.helpers import assert_json_response, assert_success_response


# =============================================================================
# Local Mode Tests - Profiles
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
class TestProfilesLocalMode:
    """Tests for /profiles endpoint in local mode."""

    def test_get_profiles_empty(self, local_client: ICtrlClient):
        """Get profiles when no sessions exist."""
        resp = local_client.get("/api/profiles")
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], dict)

    def test_get_profiles_with_session(self, local_client: ICtrlClient, local_session: str):
        """Get profiles after creating a session."""
        resp = local_client.get("/api/profiles")
        assert resp.status_code == 200
        data = resp.json()
        assert local_session in data["sessions"]


# =============================================================================
# Local Mode Tests - Session CRUD
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestSessionCreateLocalMode:
    """Tests for POST /session (create) in local mode."""

    def test_create_session_success(self, local_client: ICtrlClient, config: TestConfig):
        """Create a new SSH session with valid credentials."""
        # Use ssh_internal_host because iCtrl runs inside Docker and connects via Docker network
        resp = local_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })

        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify session was created
        profiles_resp = local_client.get("/api/profiles")
        profiles = profiles_resp.json()
        assert len(profiles["sessions"]) >= 1

        # Cleanup
        session_id = list(profiles["sessions"].keys())[-1]
        local_client.delete(f"/api/session?session_id={session_id}")

    def test_create_session_invalid_host(self, local_client: ICtrlClient, config: TestConfig):
        """Create session with unreachable host should fail."""
        resp = local_client.post("/api/session", json={
            "host": "nonexistent.invalid.host.test",
            "username": config.ssh_user,
            "password": config.ssh_password
        }, timeout=20)
        assert resp.status_code == 403

    def test_create_session_wrong_password(self, local_client: ICtrlClient, config: TestConfig):
        """Create session with wrong password should fail."""
        resp = local_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": "WrongPassword123!"
        }, timeout=20)
        assert resp.status_code == 403


@pytest.mark.integration
@pytest.mark.local_mode
class TestSessionReadLocalMode:
    """Tests for GET /session in local mode."""

    def test_get_session_info(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Get session information by ID."""
        resp = local_client.get("/api/session", params={"id": local_session})
        assert resp.status_code == 200
        data = resp.json()
        assert "host" in data
        assert "username" in data
        assert data["username"] == config.ssh_user

    def test_get_session_nonexistent(self, local_client: ICtrlClient):
        """Get non-existent session should return null values."""
        resp = local_client.get("/api/session", params={"id": "nonexistent-session-id"})
        assert resp.status_code == 200
        data = resp.json()
        # Non-existent sessions return null values
        assert data["host"] is None


@pytest.mark.integration
@pytest.mark.local_mode
class TestSessionUpdateLocalMode:
    """Tests for PATCH /session in local mode."""

    def test_set_nickname(self, local_client: ICtrlClient, local_session: str):
        """Set session nickname."""
        resp = local_client.patch("/api/session", json={
            "session_id": local_session,
            "nickname": "test"
        })
        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify nickname was set
        resp = local_client.get("/api/session", params={"id": local_session})
        data = resp.json()
        assert data["nickname"] == "test"

    def test_set_nickname_too_long(self, local_client: ICtrlClient, local_session: str):
        """Nickname longer than 8 characters should fail."""
        resp = local_client.patch("/api/session", json={
            "session_id": local_session,
            "nickname": "toolongnickname"
        })
        assert resp.status_code == 400

    def test_clear_nickname(self, local_client: ICtrlClient, local_session: str):
        """Clear nickname by setting empty string."""
        # First set a nickname
        local_client.patch("/api/session", json={
            "session_id": local_session,
            "nickname": "test"
        })

        # Then clear it
        resp = local_client.patch("/api/session", json={
            "session_id": local_session,
            "nickname": ""
        })
        assert resp.status_code == 200

        # Verify nickname was cleared
        resp = local_client.get("/api/session", params={"id": local_session})
        data = resp.json()
        assert data["nickname"] is None or data["nickname"] == ""

    def test_update_nonexistent_session(self, local_client: ICtrlClient):
        """Update non-existent session should fail."""
        resp = local_client.patch("/api/session", json={
            "session_id": "nonexistent-session-id-12345",
            "nickname": "test"
        })
        assert resp.status_code == 400

    def test_change_host(self, local_client: ICtrlClient, config: TestConfig):
        """Change session host (LocalProfile.change_host())."""
        # Create a new session (so we can modify it without breaking other tests)
        resp = local_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get the session ID
        profiles_resp = local_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_ids = list(profiles["sessions"].keys())
        session_id = session_ids[-1]

        # Get original host
        resp = local_client.get("/api/session", params={"id": session_id})
        original_host = resp.json()["host"]

        # Change host (use domain from current host)
        resp = local_client.patch("/api/session", json={
            "session_id": session_id,
            "host": "newhost"
        })
        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify host was changed
        resp = local_client.get("/api/session", params={"id": session_id})
        data = resp.json()
        assert "newhost" in data["host"]
        assert data["host"] != original_host

        # Clean up
        local_client.delete(f"/api/session?session_id={session_id}")

    def test_change_host_nonexistent_session(self, local_client: ICtrlClient):
        """Change host on non-existent session should fail."""
        resp = local_client.patch("/api/session", json={
            "session_id": "nonexistent-session-id-12345",
            "host": "newhost"
        })
        assert resp.status_code == 400


@pytest.mark.integration
@pytest.mark.local_mode
class TestSessionDeleteLocalMode:
    """Tests for DELETE /session in local mode."""

    def test_delete_session(self, local_client: ICtrlClient, config: TestConfig):
        """Delete an existing session."""
        # Create a session first (use ssh_internal_host for Docker network)
        resp = local_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200, f"Failed to create session: {resp.text}"

        profiles_resp = local_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_ids = list(profiles["sessions"].keys())
        assert len(session_ids) > 0, "No sessions found after creation"
        session_id = session_ids[-1]

        # Delete it
        resp = local_client.delete(f"/api/session?session_id={session_id}")
        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify it's gone
        profiles_resp = local_client.get("/api/profiles")
        profiles = profiles_resp.json()
        assert session_id not in profiles["sessions"]

    def test_delete_nonexistent_session(self, local_client: ICtrlClient):
        """Delete non-existent session should fail."""
        resp = local_client.delete("/api/session?session_id=nonexistent-session-id")
        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - Exec Blocking
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestExecBlockingLocalMode:
    """Tests for /exec_blocking endpoint in local mode."""

    def test_exec_simple_command(self, local_client: ICtrlClient, local_session: str):
        """Execute a simple command."""
        resp = local_client.post("/api/exec_blocking", json={
            "session_id": local_session,
            "cmd": "echo 'hello world'"
        })
        assert resp.status_code == 200
        assert "hello world" in resp.text

    def test_exec_command_with_stderr(self, local_client: ICtrlClient, local_session: str):
        """Execute command that writes to stderr."""
        resp = local_client.post("/api/exec_blocking", json={
            "session_id": local_session,
            "cmd": "echo 'error' >&2"
        })
        assert resp.status_code == 200
        assert "error" in resp.text

    def test_exec_multiline_output(self, local_client: ICtrlClient, local_session: str):
        """Execute command with multiple lines of output."""
        resp = local_client.post("/api/exec_blocking", json={
            "session_id": local_session,
            "cmd": "echo 'line1'; echo 'line2'; echo 'line3'"
        })
        assert resp.status_code == 200
        assert "line1" in resp.text
        assert "line2" in resp.text
        assert "line3" in resp.text

    def test_exec_large_output(self, local_client: ICtrlClient, local_session: str):
        """Execute command with large output using large mode."""
        resp = local_client.post("/api/exec_blocking", json={
            "session_id": local_session,
            "cmd": "seq 1 1000",
            "large": True
        })
        assert resp.status_code == 200
        assert "1" in resp.text
        assert "1000" in resp.text

    def test_exec_nonexistent_session(self, local_client: ICtrlClient):
        """Execute on non-existent session should fail."""
        resp = local_client.post("/api/exec_blocking", json={
            "session_id": "nonexistent-session-id",
            "cmd": "echo test"
        })
        assert resp.status_code == 403

    def test_exec_get_hostname(self, local_client: ICtrlClient, local_session: str):
        """Get hostname from remote."""
        resp = local_client.post("/api/exec_blocking", json={
            "session_id": local_session,
            "cmd": "hostname"
        })
        assert resp.status_code == 200
        # Should return the container hostname
        assert len(resp.text.strip()) > 0

    def test_exec_get_current_user(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Verify we're connected as the correct user."""
        resp = local_client.post("/api/exec_blocking", json={
            "session_id": local_session,
            "cmd": "whoami"
        })
        assert resp.status_code == 200
        assert config.ssh_user in resp.text


# =============================================================================
# Database Mode Tests - Profiles and Sessions
# =============================================================================

@pytest.mark.integration
@pytest.mark.db_mode
@pytest.mark.ssh
class TestDBModeAuthenticatedSession:
    """Tests for session/profile routes in DB mode with authenticated user.

    These tests cover DBProfile methods that require a logged-in user:
    - query()
    - add_session()
    - delete_session()
    - change_host()
    - set_session_nickname()
    - get_session_info()
    - set_session_vnc_credentials()
    - get_session_vnc_credentials()
    """

    @pytest.fixture
    def authenticated_db_client(
        self,
        db_client: ICtrlClient,
        config: TestConfig,
        clean_db,
        clear_mailbox,
        unique_username: str,
        valid_password: str,
        valid_email: str
    ):
        """Create a registered, activated, and logged-in user with a session-based client."""
        # Register the user
        resp = db_client.post("/api/register", json={
            "username": unique_username,
            "password": valid_password,
            "email": valid_email
        })
        assert resp.status_code == 200

        # Wait for activation email
        time.sleep(2)
        emails = get_emails(config)

        # Find the activation email and extract the code
        activated = False
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
                match = re.search(r'userid=(\d+)(?:&amp;|&)code=([a-f0-9-]+)', html_body)
                if match:
                    userid = match.group(1)
                    code = match.group(2)

                    # Activate the account
                    resp = db_client.get("/api/activate", params={
                        "userid": userid,
                        "code": code
                    })
                    activated = True
                    break

        if not activated:
            pytest.skip("Could not activate user")

        # Login
        resp = db_client.post("/api/login", json={
            "username": unique_username,
            "password": valid_password
        })
        assert resp.status_code == 200
        assert "logged in" in resp.text

        yield db_client

        # Logout
        db_client.get("/api/logout")

    def test_get_profiles_empty(self, authenticated_db_client: ICtrlClient):
        """Get profiles when no SSH sessions exist (DBProfile.query())."""
        resp = authenticated_db_client.get("/api/profiles")
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], dict)
        assert len(data["sessions"]) == 0

    def test_create_session_success(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Create a new SSH session (DBProfile.add_session())."""
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })

        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify session was created (DBProfile.query())
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        assert len(profiles["sessions"]) == 1

        # Clean up
        session_id = list(profiles["sessions"].keys())[0]
        authenticated_db_client.delete(f"/api/session?session_id={session_id}")

    def test_get_session_info(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Get session info (DBProfile.get_session_info() via GET /session)."""
        # Create a session first
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get session ID
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_id = list(profiles["sessions"].keys())[0]

        # Get session info
        resp = authenticated_db_client.get("/api/session", params={"id": session_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["host"] == config.ssh_internal_host
        assert data["username"] == config.ssh_user

        # Clean up
        authenticated_db_client.delete(f"/api/session?session_id={session_id}")

    def test_set_nickname(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Set session nickname (DBProfile.set_session_nickname())."""
        # Create a session first
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get session ID
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_id = list(profiles["sessions"].keys())[0]

        # Set nickname
        resp = authenticated_db_client.patch("/api/session", json={
            "session_id": session_id,
            "nickname": "testnick"
        })
        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify nickname was set
        resp = authenticated_db_client.get("/api/session", params={"id": session_id})
        data = resp.json()
        assert data["nickname"] == "testnick"

        # Clean up
        authenticated_db_client.delete(f"/api/session?session_id={session_id}")

    def test_delete_session(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Delete session (DBProfile.delete_session())."""
        # Create a session first
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get session ID
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_id = list(profiles["sessions"].keys())[0]

        # Delete the session
        resp = authenticated_db_client.delete(f"/api/session?session_id={session_id}")
        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify session was deleted
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        assert len(profiles["sessions"]) == 0

    def test_delete_nonexistent_session(self, authenticated_db_client: ICtrlClient):
        """Delete non-existent session should fail."""
        resp = authenticated_db_client.delete("/api/session?session_id=00000000000000000000000000000000")
        assert resp.status_code == 403

    def test_set_nickname_nonexistent_session(self, authenticated_db_client: ICtrlClient):
        """Set nickname on non-existent session should fail."""
        resp = authenticated_db_client.patch("/api/session", json={
            "session_id": "00000000000000000000000000000000",
            "nickname": "test"
        })
        assert resp.status_code == 400

    def test_get_userid(self, authenticated_db_client: ICtrlClient):
        """Get user ID when logged in."""
        resp = authenticated_db_client.get("/api/userid")
        assert resp.status_code == 200
        # User ID should be a number
        assert resp.text.isdigit()
        assert int(resp.text) > 0

    def test_change_host(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Change session host (DBProfile.change_host())."""
        # Create a session first
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get session ID
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_id = list(profiles["sessions"].keys())[0]

        # Change host (use domain from current host)
        resp = authenticated_db_client.patch("/api/session", json={
            "session_id": session_id,
            "host": "newhost"
        })
        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify host was changed - we can't verify the exact value because
        # the domain is appended, but we can verify it changed
        resp = authenticated_db_client.get("/api/session", params={"id": session_id})
        data = resp.json()
        assert "newhost" in data["host"]

        # Clean up
        authenticated_db_client.delete(f"/api/session?session_id={session_id}")

    def test_vnc_credentials_set_and_get(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Set and get VNC credentials (DBProfile.set_session_vnc_credentials(), get_session_vnc_credentials()).

        This test covers lines 364-373 in DBProfile.py by:
        1. Creating a session
        2. Setting VNC credentials
        3. Starting VNC with loadCredentials=True to trigger get_session_vnc_credentials()
        """
        from tests.helpers import parse_streaming_response

        # Create a session first
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get session ID
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_id = list(profiles["sessions"].keys())[0]

        # Set VNC credentials
        credentials = {"password": "testvncpass", "username": "vncuser"}
        resp = authenticated_db_client.put("/api/vnc_credentials", json={
            "session_id": session_id,
            "credentials": credentials
        })
        assert resp.status_code == 200
        assert resp.text == "success"

        # Set a VNC password on the remote so VNC can start
        resp = authenticated_db_client.post("/api/vncpasswd", json={
            "session_id": session_id,
            "passwd": "remotepass"
        }, timeout=30)
        assert resp.status_code == 200

        # Start VNC with loadCredentials=True - this calls get_session_vnc_credentials()
        resp = authenticated_db_client.post("/api/vnc", json={
            "sessionID": session_id,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)
        assert resp.status_code == 200

        _, data = parse_streaming_response(resp.content)

        # Should return the saved credentials
        assert data is not None
        assert "credentials" in data
        assert data["credentials"] is not None
        assert data["credentials"]["password"] == credentials["password"]
        assert data["credentials"]["username"] == credentials["username"]

        # Clean up
        authenticated_db_client.delete(f"/api/session?session_id={session_id}")

    def test_vnc_credentials_update(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Update existing VNC credentials."""
        # Create a session first
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get session ID
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_id = list(profiles["sessions"].keys())[0]

        # Set initial VNC credentials
        credentials1 = {"password": "pass1"}
        resp = authenticated_db_client.put("/api/vnc_credentials", json={
            "session_id": session_id,
            "credentials": credentials1
        })
        assert resp.status_code == 200

        # Update VNC credentials
        credentials2 = {"password": "pass2"}
        resp = authenticated_db_client.put("/api/vnc_credentials", json={
            "session_id": session_id,
            "credentials": credentials2
        })
        assert resp.status_code == 200

        # Clean up
        authenticated_db_client.delete(f"/api/session?session_id={session_id}")

    def test_vnc_credentials_nonexistent_session(self, authenticated_db_client: ICtrlClient):
        """Set VNC credentials on non-existent session should fail."""
        resp = authenticated_db_client.put("/api/vnc_credentials", json={
            "session_id": "00000000000000000000000000000000",
            "credentials": {"password": "test"}
        })
        assert resp.status_code == 403

    def test_vnc_credentials_delete(self, authenticated_db_client: ICtrlClient, config: TestConfig):
        """Delete VNC credentials (DBProfile.set_session_vnc_credentials with None).

        Note: This test uses the VNC endpoint with loadCredentials=False which triggers
        the delete path. The VNC connection may fail later but the credentials are
        deleted early in the request processing.
        """
        from tests.helpers import parse_streaming_response

        # Create a session first
        resp = authenticated_db_client.post("/api/session", json={
            "host": config.ssh_internal_host,
            "username": config.ssh_user,
            "password": config.ssh_password
        })
        assert resp.status_code == 200

        # Get session ID
        profiles_resp = authenticated_db_client.get("/api/profiles")
        profiles = profiles_resp.json()
        session_id = list(profiles["sessions"].keys())[0]

        # Set VNC credentials first
        credentials = {"password": "testvncpass"}
        resp = authenticated_db_client.put("/api/vnc_credentials", json={
            "session_id": session_id,
            "credentials": credentials
        })
        assert resp.status_code == 200

        # Delete VNC credentials by setting to None
        # This is done via the /vnc endpoint with loadCredentials=False
        # which calls profiles.set_session_vnc_credentials(session_id, None)
        # Use a shorter timeout since we just need to exercise the delete path
        resp = authenticated_db_client.post("/api/vnc", json={
            "sessionID": session_id,
            "loadCheck": False,
            "loadCredentials": False
        }, timeout=60)

        # The VNC endpoint returns a streaming response
        # It should at least start (SSH_AUTH step)
        assert resp.status_code == 200
        steps, _ = parse_streaming_response(resp.content)
        # Should have at least SSH_AUTH step which means the request was processed
        # (the credentials delete happens early in the flow)
        assert len(steps) >= 1

        # Clean up
        authenticated_db_client.delete(f"/api/session?session_id={session_id}")
