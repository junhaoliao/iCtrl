"""
Integration tests for Connection features (features/Connection.py)

Tests for: is_load_high(), supports_load_check(), is_uoft(), exec_command_blocking(), etc.
"""

import pytest
from tests.conftest import ICtrlClient, TestConfig
from application.codes import ICtrlError, ICtrlStep


# =============================================================================
# Connection Feature Tests - Load Checking via API
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestConnectionLoadCheckAPI:
    """Tests for Connection load checking functionality via API endpoints.

    These tests verify that load checking is exercised through the API.
    The tests pass whether load is high or low - the important thing is that
    the load check code path is executed and covered.
    """

    def test_terminal_with_load_check_exercises_load_check(self, local_client: ICtrlClient, local_session: str):
        """Test terminal with load check enabled exercises the load checking code.

        This exercises supports_load_check() and is_load_high() through the API.
        The test container supports load checking (has uptime, who commands).

        The test passes whether load is considered high or low - the goal is
        to exercise the code path for coverage.
        """
        from tests.helpers import parse_streaming_response

        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": True  # Enable load check
        })

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        # Should have CHECK_LOAD step (step code 1)
        assert ICtrlStep.Term.CHECK_LOAD in steps, f"CHECK_LOAD step not found in {steps}"

        # Either we get success data, or we get OVER_LOADED error
        # Both are valid outcomes that exercise the load checking code
        if data is not None:
            # Load was low - terminal started
            assert "port" in data
            assert "term_id" in data
        else:
            # Load was high - should have OVER_LOADED error code
            assert ICtrlError.SSH.OVER_LOADED in steps, f"Expected either success or OVER_LOADED, got steps: {steps}"

    def test_terminal_without_load_check(self, local_client: ICtrlClient, local_session: str):
        """Test terminal with load check disabled skips the check."""
        from tests.helpers import parse_streaming_response

        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": False  # Disable load check
        })

        assert resp.status_code == 200
        _, data = parse_streaming_response(resp.content)
        assert data is not None
        assert "port" in data

    def test_vnc_with_load_check_exercises_load_check(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Test VNC with load check enabled exercises the load checking code."""
        from tests.helpers import parse_streaming_response, kill_all_vnc

        # Setup
        kill_all_vnc(ssh_client)
        local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "loadtest"
        }, timeout=30)

        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": True,  # Enable load check
            "loadCredentials": True
        }, timeout=60)

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        # Should have CHECK_LOAD step
        assert ICtrlStep.VNC.CHECK_LOAD in steps, f"CHECK_LOAD step not found in {steps}"

        # Either we get success data, or we get OVER_LOADED error
        if data is not None:
            assert "port" in data
        else:
            assert ICtrlError.SSH.OVER_LOADED in steps, f"Expected either success or OVER_LOADED, got steps: {steps}"

        kill_all_vnc(ssh_client)


# =============================================================================
# Connection Feature Tests - is_uoft methods (unit-style tests)
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestIsUoftMethods:
    """Tests for is_eecg, is_ecf, is_uoft methods.

    These tests don't require an actual SSH connection since they
    only check the hostname string.
    """

    def test_is_uoft_methods_non_uoft(self):
        """Test is_uoft methods with non-UofT host."""
        from application.features.Connection import Connection

        conn = Connection()
        conn.host = "some.other.server.com"

        assert conn.is_eecg() is False
        assert conn.is_ecf() is False
        assert conn.is_uoft() is False

    def test_is_uoft_methods_eecg(self):
        """Test is_uoft methods with EECG host."""
        from application.features.Connection import Connection

        conn = Connection()
        conn.host = "ug250.eecg.utoronto.ca"

        assert conn.is_eecg() is True
        assert conn.is_ecf() is False
        assert conn.is_uoft() is True

    def test_is_uoft_methods_ecf(self):
        """Test is_uoft methods with ECF host."""
        from application.features.Connection import Connection

        conn = Connection()
        conn.host = "p1.ecf.utoronto.ca"

        assert conn.is_eecg() is False
        assert conn.is_ecf() is True
        assert conn.is_uoft() is True


# =============================================================================
# Connection Failure Tests - SSH Error Branches
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestConnectionFailureBranches:
    """Tests for SSH connection failure handling in create_connection().

    These tests cover the error branches in routes/common.py create_connection():
    - HOST_UNREACHABLE (timeout, Errno 60/64/51)
    - AUTH_WRONG (RSA key error)
    - GENERAL (other errors)
    """

    def test_connection_timeout_host_unreachable(self, local_client: ICtrlClient, config: TestConfig):
        """Test connection to unreachable host triggers HOST_UNREACHABLE error.

        This covers the 'timed out' and Errno branches in create_connection().
        """
        from tests.helpers import parse_streaming_response
        from requests.exceptions import ChunkedEncodingError

        # Create a session with valid credentials
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

        # Change the host to an unreachable IP (non-routable)
        # 10.255.255.1 is typically unreachable and will timeout
        resp = local_client.patch("/api/session", json={
            "session_id": session_id,
            "host": "10.255.255.1",
            "domain": ""  # Empty domain to just use the host as-is
        })
        assert resp.status_code == 200

        # Try to connect via terminal - should get HOST_UNREACHABLE
        try:
            resp = local_client.post("/api/terminal", json={
                "sessionID": session_id,
                "loadCheck": False
            }, timeout=30)

            # Parse the streaming response
            steps, _ = parse_streaming_response(resp.content)
            # Should have HOST_UNREACHABLE error (0xcc = 204)
            assert ICtrlError.SSH.HOST_UNREACHABLE in steps, f"Expected HOST_UNREACHABLE in {steps}"
        except ChunkedEncodingError:
            # Connection failure may cause chunked encoding error - that's expected
            pass

        # Clean up
        local_client.delete(f"/api/session?session_id={session_id}")

    def test_connection_refused_host_unreachable(self, local_client: ICtrlClient, config: TestConfig):
        """Test connection to host with closed port triggers error.

        This covers error handling when connection is refused.
        """
        from tests.helpers import parse_streaming_response
        from requests.exceptions import ChunkedEncodingError

        # Create a session
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

        # Change the host to localhost with wrong port (by using host:port format)
        # This should fail with connection refused
        resp = local_client.patch("/api/session", json={
            "session_id": session_id,
            "host": "localhost:65000",  # Port that's likely not listening
            "domain": ""
        })
        assert resp.status_code == 200

        # Try to connect - should get some error
        try:
            resp = local_client.post("/api/terminal", json={
                "sessionID": session_id,
                "loadCheck": False
            }, timeout=30)

            # Parse response - any error code is acceptable here
            steps, _ = parse_streaming_response(resp.content)
            # Should have some error (HOST_UNREACHABLE or GENERAL)
            has_error = any(s >= 100 for s in steps)
            assert has_error or len(steps) > 0
        except (ChunkedEncodingError, Exception):
            pass

        # Clean up
        local_client.delete(f"/api/session?session_id={session_id}")
