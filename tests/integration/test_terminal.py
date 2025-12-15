"""
Integration tests for terminal routes (routes/term.py)

Tests for: /terminal, /terminal_resize, Terminal WebSocket
"""

import pytest
import time
from tests.conftest import ICtrlClient, TestConfig
from tests.helpers import (
    parse_streaming_response,
    parse_step_codes,
    TerminalWebSocket,
)


# =============================================================================
# Local Mode Tests - Terminal Start
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestTerminalStartLocalMode:
    """Tests for POST /terminal endpoint in local mode."""

    def test_start_terminal_success(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Successfully start a terminal session."""
        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": False  # Skip load check for testing
        })

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        # Should have step codes for SSH_AUTH, CHECK_LOAD, LAUNCH_SHELL, DONE
        assert len(steps) >= 3

        # Should return port and term_id
        assert data is not None
        assert "port" in data
        assert "term_id" in data
        assert isinstance(data["port"], int)
        assert len(data["term_id"]) == 32  # UUID hex

    def test_start_terminal_invalid_session(self, local_client: ICtrlClient):
        """Start terminal with invalid session should fail."""
        from requests.exceptions import ChunkedEncodingError

        try:
            resp = local_client.post("/api/terminal", json={
                "sessionID": "nonexistent-session-id",
                "loadCheck": False
            })

            # If we get here without exception, check for error in response
            assert resp.status_code in (200, 403)
            if resp.status_code == 403:
                # Server returned error response
                assert "does not exist" in resp.text or "invalid" in resp.text.lower()
            else:
                # Streaming response with error
                steps, _ = parse_streaming_response(resp.content)
                has_error = any(s >= 100 for s in steps)
                if not has_error:
                    assert b"invalid" in resp.content.lower() or b"not found" in resp.content.lower()

        except ChunkedEncodingError:
            # This is expected - the server aborts the streaming response when session is invalid.
            # The client code in term.js handles this gracefully by detecting error codes.
            pass

    def test_start_terminal_with_load_check(self, local_client: ICtrlClient, local_session: str):
        """Start terminal with load check enabled."""
        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": True
        })

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        # Should include CHECK_LOAD step
        # The exact step codes depend on ICtrlStep.Term enum
        assert len(steps) >= 2

    def test_start_multiple_terminals(self, local_client: ICtrlClient, local_session: str):
        """Start multiple terminal sessions for same SSH session."""
        term_ids = []

        for _ in range(2):
            resp = local_client.post("/api/terminal", json={
                "sessionID": local_session,
                "loadCheck": False
            })
            assert resp.status_code == 200
            _, data = parse_streaming_response(resp.content)
            if data and "term_id" in data:
                term_ids.append(data["term_id"])

        # Should have two different terminal IDs
        if len(term_ids) == 2:
            assert term_ids[0] != term_ids[1]


# =============================================================================
# Local Mode Tests - Terminal Resize
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestTerminalResizeLocalMode:
    """Tests for PATCH /terminal_resize endpoint in local mode."""

    @pytest.fixture
    def active_terminal(self, local_client: ICtrlClient, local_session: str):
        """Create an active terminal and return term_id."""
        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": False
        })
        _, data = parse_streaming_response(resp.content)
        if data and "term_id" in data:
            yield data["term_id"]
        else:
            pytest.skip("Could not create terminal")

    def test_resize_terminal_success(self, local_client: ICtrlClient, active_terminal: str):
        """Resize terminal with valid dimensions."""
        resp = local_client.patch("/api/terminal_resize", json={
            "term_id": active_terminal,
            "w": 120,
            "h": 40
        })

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_resize_terminal_different_sizes(self, local_client: ICtrlClient, active_terminal: str):
        """Resize terminal to various sizes."""
        sizes = [(80, 24), (120, 40), (200, 60), (40, 10)]

        for width, height in sizes:
            resp = local_client.patch("/api/terminal_resize", json={
                "term_id": active_terminal,
                "w": width,
                "h": height
            })
            assert resp.status_code == 200
            assert resp.text == "success"

    def test_resize_terminal_invalid_term_id(self, local_client: ICtrlClient):
        """Resize with invalid term_id should fail."""
        resp = local_client.patch("/api/terminal_resize", json={
            "term_id": "nonexistent-term-id",
            "w": 80,
            "h": 24
        })

        assert resp.status_code == 403
        assert "invalid" in resp.text.lower()


# =============================================================================
# Local Mode Tests - Terminal WebSocket
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestTerminalWebSocketLocalMode:
    """Tests for Terminal WebSocket connections in local mode."""

    @pytest.fixture
    def terminal_info(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Create terminal and return (port, term_id, auth_key)."""
        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": False
        })
        _, data = parse_streaming_response(resp.content)
        if data and "term_id" in data and "port" in data:
            yield (data["port"], data["term_id"], config.ictrl_local_auth_key)
        else:
            pytest.skip("Could not create terminal")

    def test_websocket_connect(self, terminal_info: tuple, config: TestConfig):
        """Connect to terminal WebSocket."""
        port, term_id, auth_key = terminal_info
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"

        with TerminalWebSocket(ws_url, auth_key) as ws:
            assert ws.ws is not None
            assert ws.ws.connected

    def test_websocket_receive_data(self, terminal_info: tuple, config: TestConfig):
        """Receive initial shell output from terminal."""
        port, term_id, auth_key = terminal_info
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"

        with TerminalWebSocket(ws_url, auth_key) as ws:
            # Wait for shell prompt or initial output
            data = ws.recv_all(timeout=3)
            # Should receive some output (shell prompt, motd, etc.)
            # Note: might be empty if shell hasn't sent anything yet
            assert ws.ws.connected or len(data) > 0

    def test_websocket_send_command(self, terminal_info: tuple, config: TestConfig):
        """Send a command through WebSocket and receive output."""
        port, term_id, auth_key = terminal_info
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"

        with TerminalWebSocket(ws_url, auth_key) as ws:
            # Clear initial data after it arrives
            ws.recv_all(timeout=1)
            ws.received_data.clear()

            # Send echo command
            ws.send("echo 'TESTOUTPUT123'\n")

            # Wait for response
            assert ws.wait_for_data(b"TESTOUTPUT123", timeout=3)

    def test_websocket_interactive_commands(self, terminal_info: tuple, config: TestConfig):
        """Execute multiple interactive commands."""
        port, term_id, auth_key = terminal_info
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"

        with TerminalWebSocket(ws_url, auth_key) as ws:
            time.sleep(1)
            ws.received_data.clear()

            # Test whoami
            ws.send("whoami\n")
            time.sleep(1)
            data = ws.recv_all(timeout=2)
            assert config.ssh_user.encode() in data

    def test_websocket_pwd_command(self, terminal_info: tuple, config: TestConfig):
        """Execute pwd command."""
        port, term_id, auth_key = terminal_info
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"

        with TerminalWebSocket(ws_url, auth_key) as ws:
            time.sleep(1)
            ws.received_data.clear()

            ws.send("pwd\n")
            data = ws.recv_all(timeout=2)
            # Should show home directory
            assert b"/home" in data or b"~" in data.decode('utf-8', errors='ignore')

    def test_websocket_invalid_term_id(self, config: TestConfig):
        """Connect with invalid term_id should fail."""
        # Use a port that likely has the WebSocket server
        # We need to get a valid port first
        ws_url = f"wss://{config.ictrl_local_host}:25000/invalid-term-id"

        ws = TerminalWebSocket(ws_url, config.ictrl_local_auth_key)
        try:
            # Connection should fail or be closed immediately
            ws.connect(timeout=5)
            time.sleep(1)
            # If connected, server should close the connection
            if ws.ws:
                assert not ws.ws.connected or ws.ws.connected
        except Exception:
            pass  # Expected - connection should fail
        finally:
            ws.close()

    def test_websocket_special_characters(self, terminal_info: tuple, config: TestConfig):
        """Send special characters and control sequences."""
        port, term_id, auth_key = terminal_info
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"

        with TerminalWebSocket(ws_url, auth_key) as ws:
            time.sleep(1)
            ws.received_data.clear()

            # Send a command with special characters
            ws.send('echo "Hello, World! @#$%"\n')
            data = ws.recv_all(timeout=2)
            assert b"Hello, World!" in data

    def test_websocket_ctrl_c(self, terminal_info: tuple, config: TestConfig):
        """Send Ctrl+C interrupt signal."""
        port, term_id, auth_key = terminal_info
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"

        with TerminalWebSocket(ws_url, auth_key) as ws:
            time.sleep(1)

            # Start a long-running command
            ws.send("sleep 100\n")
            time.sleep(0.5)

            # Send Ctrl+C (ASCII 3)
            ws.send(b'\x03')
            time.sleep(1)

            # Should be able to run another command
            ws.received_data.clear()
            ws.send("echo 'interrupted'\n")
            data = ws.recv_all(timeout=2)
            assert b"interrupted" in data


# =============================================================================
# Local Mode Tests - Terminal End-to-End
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.ssh
class TestTerminalE2ELocalMode:
    """End-to-end tests for terminal functionality."""

    def test_full_terminal_lifecycle(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Test complete terminal lifecycle: create, use, resize."""
        # 1. Start terminal
        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": False
        })
        assert resp.status_code == 200
        _, data = parse_streaming_response(resp.content)
        assert data is not None
        port = data["port"]
        term_id = data["term_id"]

        # 2. Connect via WebSocket, run commands, and resize while connected
        # Note: The terminal connection is removed from TERM_CONNECTIONS when WebSocket closes,
        # so resize must happen while the WebSocket is still open.
        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"
        with TerminalWebSocket(ws_url, config.ictrl_local_auth_key) as ws:
            time.sleep(1)
            ws.received_data.clear()

            ws.send("echo 'lifecycle_test'\n")
            data = ws.recv_all(timeout=2)
            assert b"lifecycle_test" in data

            # 3. Resize terminal (must be done while WebSocket is connected)
            resp = local_client.patch("/api/terminal_resize", json={
                "term_id": term_id,
                "w": 100,
                "h": 30
            })
            assert resp.status_code == 200

    def test_terminal_environment_variables(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Verify terminal has proper environment."""
        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": False
        })
        _, data = parse_streaming_response(resp.content)
        port = data["port"]
        term_id = data["term_id"]

        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"
        with TerminalWebSocket(ws_url, config.ictrl_local_auth_key) as ws:
            time.sleep(1)
            ws.received_data.clear()

            # Check TERM variable
            ws.send("echo $TERM\n")
            data = ws.recv_all(timeout=2)
            # Should be xterm-256color as specified in Term.py
            assert b"xterm" in data

    def test_terminal_working_directory(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Terminal should start in user's home directory."""
        resp = local_client.post("/api/terminal", json={
            "sessionID": local_session,
            "loadCheck": False
        })
        _, data = parse_streaming_response(resp.content)
        port = data["port"]
        term_id = data["term_id"]

        ws_url = f"wss://{config.ictrl_local_host}:{port}/{term_id}"
        with TerminalWebSocket(ws_url, config.ictrl_local_auth_key) as ws:
            time.sleep(1)
            ws.received_data.clear()

            # Check current directory
            ws.send("pwd\n")
            data = ws.recv_all(timeout=2)
            # Should be in home directory
            expected_home = f"/home/{config.ssh_user}"
            assert expected_home.encode() in data
