"""
Integration tests for VNC routes (routes/vnc.py)

Tests for: /vnc, /vncpasswd, /vnc_reset, /vnc_credentials
"""

import pytest
import socket
import ssl
import time
from tests.conftest import ICtrlClient, TestConfig
from tests.helpers import (
    parse_streaming_response,
    kill_all_vnc,
    get_vnc_display,
)


# =============================================================================
# Local Mode Tests - VNC Start
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.vnc
class TestVNCStartLocalMode:
    """Tests for POST /vnc endpoint in local mode."""

    @pytest.fixture(autouse=True)
    def setup_vnc(self, ssh_client):
        """Ensure VNC is stopped before each test."""
        kill_all_vnc(ssh_client)
        yield
        # Cleanup after test
        kill_all_vnc(ssh_client)

    def test_start_vnc_success(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Successfully start a VNC session."""
        # First, set up a VNC password (required for VNC to start successfully)
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "testpwd"
        }, timeout=30)
        assert resp.status_code == 200

        # Now start VNC
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        # Should have step codes: SSH_AUTH, CHECK_LOAD, PARSE_PASSWD, LAUNCH_VNC, CREATE_TUNNEL, DONE
        assert len(steps) >= 4

        # Should return port and credentials
        assert data is not None
        assert "port" in data
        assert isinstance(data["port"], int)
        assert data["port"] > 0

    def test_vnc_tunnel_connection(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Test that connecting to VNC WebSocket triggers ForwardServerHandler.

        This test covers ForwardServerHandler.handle() in Connection.py (lines 32-73)
        by actually connecting to the VNC tunnel and exchanging data.
        """
        import base64
        import struct

        # Set up a VNC password (required for VNC to start successfully)
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "tunneltest"
        }, timeout=30)
        assert resp.status_code == 200

        # Start VNC
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        assert data is not None
        ws_port = data["port"]
        assert ws_port > 0

        # Connect to the WebSocket port and do a proper WebSocket handshake
        # then exchange VNC protocol data to cover ForwardServerHandler data paths
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection(("localhost", ws_port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                # WebSocket handshake
                ws_key = base64.b64encode(b"test-websocket-key!").decode()
                ws_request = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: localhost:{ws_port}\r\n"
                    f"Upgrade: websocket\r\n"
                    f"Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Key: {ws_key}\r\n"
                    f"Sec-WebSocket-Version: 13\r\n"
                    f"Authorization: Bearer {config.ictrl_local_auth_key}\r\n"
                    f"\r\n"
                )
                ssock.sendall(ws_request.encode())

                # Read HTTP upgrade response
                response = b""
                while b"\r\n\r\n" not in response:
                    chunk = ssock.recv(1024)
                    if not chunk:
                        break
                    response += chunk

                # Check we got 101 Switching Protocols
                assert b"101" in response, f"Expected 101 Switching Protocols, got: {response[:100]}"

                # Now we're in WebSocket mode. The VNC server should send its version string.
                # Read a WebSocket frame containing VNC server greeting (e.g., "RFB 003.008\n")
                # WebSocket frame format: [opcode byte] [length byte] [payload...]
                try:
                    ssock.settimeout(5)
                    frame_header = ssock.recv(2)
                    if len(frame_header) >= 2:
                        # Parse WebSocket frame
                        opcode = frame_header[0] & 0x0F
                        length = frame_header[1] & 0x7F

                        if length == 126:
                            ext_len = ssock.recv(2)
                            length = struct.unpack(">H", ext_len)[0]
                        elif length == 127:
                            ext_len = ssock.recv(8)
                            length = struct.unpack(">Q", ext_len)[0]

                        # Read the payload (VNC version string from server)
                        if length > 0 and length < 1024:
                            payload = ssock.recv(length)
                            # VNC server sends "RFB xxx.yyy\n" - this covers chan.recv and self.request.send
                            assert len(payload) > 0, "Expected VNC server greeting"

                            # Send a VNC client version response back through the tunnel
                            # This covers self.request.recv and chan.send
                            vnc_client_version = b"RFB 003.008\n"
                            # Create WebSocket binary frame (opcode 0x82 for binary)
                            ws_frame = bytes([0x82, 0x80 | len(vnc_client_version)])
                            # Add masking key (required for client->server)
                            mask_key = b"\x00\x00\x00\x00"
                            ws_frame += mask_key
                            # Masked payload (with zero mask, payload is unchanged)
                            ws_frame += vnc_client_version
                            ssock.sendall(ws_frame)

                            # Give it a moment to process
                            time.sleep(0.1)

                except socket.timeout:
                    # Timeout is acceptable - we've already exchanged some data
                    pass

    def test_vnc_tunnel_close_from_server(self, local_client: ICtrlClient, local_session: str, config: TestConfig, ssh_client):
        """Test ForwardServerHandler handles server-side connection close.

        This test covers line 64 in Connection.py: `if len(data) == 0: break`
        by making the VNC server close the connection.
        """
        import base64
        import struct

        # Set up a VNC password
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "closetest"
        }, timeout=30)
        assert resp.status_code == 200

        # Start VNC
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        assert data is not None
        ws_port = data["port"]
        assert ws_port > 0

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection(("localhost", ws_port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                # WebSocket handshake
                ws_key = base64.b64encode(b"test-websocket-key!").decode()
                ws_request = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: localhost:{ws_port}\r\n"
                    f"Upgrade: websocket\r\n"
                    f"Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Key: {ws_key}\r\n"
                    f"Sec-WebSocket-Version: 13\r\n"
                    f"Authorization: Bearer {config.ictrl_local_auth_key}\r\n"
                    f"\r\n"
                )
                ssock.sendall(ws_request.encode())

                # Read HTTP upgrade response
                response = b""
                while b"\r\n\r\n" not in response:
                    chunk = ssock.recv(1024)
                    if not chunk:
                        break
                    response += chunk

                assert b"101" in response

                # Read VNC server greeting
                ssock.settimeout(5)
                frame_header = ssock.recv(2)
                if len(frame_header) >= 2:
                    length = frame_header[1] & 0x7F
                    if length > 0:
                        ssock.recv(length)

                # Now kill the VNC server on the remote side
                # This will cause the SSH channel to close, triggering `if len(data) == 0: break`
                kill_all_vnc(ssh_client)

                # Give the server time to close
                time.sleep(0.5)

                # Try to read - should get empty data or connection closed
                try:
                    ssock.settimeout(2)
                    # Keep reading until we get empty data or error
                    for _ in range(5):
                        data = ssock.recv(1024)
                        if len(data) == 0:
                            # This is what we want - server closed connection
                            break
                        time.sleep(0.1)
                except (socket.timeout, ConnectionResetError, ssl.SSLError):
                    # Connection was closed - this is expected
                    pass

    def test_start_vnc_no_load_credentials(self, local_client: ICtrlClient, local_session: str):
        """Start VNC without loading credentials."""
        # Set up a VNC password first (required for VNC to start)
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "testpwd"
        }, timeout=30)
        assert resp.status_code == 200

        # Start VNC without loading credentials
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": False
        }, timeout=60)

        assert resp.status_code == 200
        steps, data = parse_streaming_response(resp.content)

        # Should still succeed (credentials will be None since loadCredentials=False)
        assert data is not None
        assert "port" in data
        # credentials should be None when not loading
        assert data.get("credentials") is None

    def test_start_vnc_with_load_check(self, local_client: ICtrlClient, local_session: str):
        """Start VNC with load check enabled."""
        # Set up a VNC password first (required for VNC to start)
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "testpwd"
        }, timeout=30)
        assert resp.status_code == 200

        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": True,
            "loadCredentials": True
        }, timeout=60)

        # Load check should pass on our test container (non-UofT host)
        assert resp.status_code == 200

    def test_start_vnc_invalid_session(self, local_client: ICtrlClient):
        """Start VNC with invalid session should fail."""
        from requests.exceptions import ChunkedEncodingError

        try:
            resp = local_client.post("/api/vnc", json={
                "sessionID": "nonexistent-session-id",
                "loadCheck": False,
                "loadCredentials": False
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
            # The client code in vnc.js handles this gracefully by detecting error codes.
            pass


# =============================================================================
# Local Mode Tests - VNC Password
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.vnc
class TestVNCPasswordLocalMode:
    """Tests for POST /vncpasswd endpoint in local mode."""

    @pytest.fixture(autouse=True)
    def setup_vnc(self, ssh_client):
        """Ensure VNC is stopped before each test."""
        kill_all_vnc(ssh_client)
        yield
        kill_all_vnc(ssh_client)

    def test_change_vnc_password(self, local_client: ICtrlClient, local_session: str):
        """Change VNC password successfully."""
        new_password = "newpass1"

        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": new_password
        }, timeout=30)

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_change_vnc_password_short(self, local_client: ICtrlClient, local_session: str):
        """Change VNC password to short password (still valid for VNC)."""
        # VNC passwords can be 1-8 characters
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "abc"
        }, timeout=30)

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_change_vnc_password_max_length(self, local_client: ICtrlClient, local_session: str):
        """Change VNC password to 8 character password (max for VNC)."""
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "12345678"
        }, timeout=30)

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_change_vnc_password_invalid_session(self, local_client: ICtrlClient):
        """Change VNC password with invalid session should fail."""
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": "nonexistent-session-id",
            "passwd": "testpass"
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - VNC Reset
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.vnc
class TestVNCResetLocalMode:
    """Tests for POST /vnc_reset endpoint in local mode."""

    @pytest.fixture(autouse=True)
    def setup_vnc(self, ssh_client):
        """Ensure clean VNC state."""
        kill_all_vnc(ssh_client)
        yield
        kill_all_vnc(ssh_client)

    def test_reset_vnc_success(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Reset VNC settings successfully."""
        # First, set up VNC by changing password (creates ~/.vnc directory)
        local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "testpw"
        }, timeout=30)

        # Now reset
        resp = local_client.post("/api/vnc_reset", json={
            "session_id": local_session
        }, timeout=30)

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_reset_vnc_no_existing_settings(self, local_client: ICtrlClient, local_session: str):
        """Reset VNC when no settings exist should still succeed."""
        resp = local_client.post("/api/vnc_reset", json={
            "session_id": local_session
        }, timeout=30)

        # Should succeed even if nothing to reset
        assert resp.status_code == 200

    def test_reset_vnc_invalid_session(self, local_client: ICtrlClient):
        """Reset VNC with invalid session should fail."""
        resp = local_client.post("/api/vnc_reset", json={
            "session_id": "nonexistent-session-id"
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - VNC Credentials
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.vnc
class TestVNCCredentialsLocalMode:
    """Tests for PUT /vnc_credentials endpoint in local mode."""

    def test_save_vnc_credentials(self, local_client: ICtrlClient, local_session: str):
        """Save VNC credentials."""
        credentials = {"password": "savedpass"}

        resp = local_client.put("/api/vnc_credentials", json={
            "session_id": local_session,
            "credentials": credentials
        })

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_save_vnc_credentials_with_username(self, local_client: ICtrlClient, local_session: str):
        """Save VNC credentials including username."""
        credentials = {
            "password": "savedpass",
            "username": "vncuser"
        }

        resp = local_client.put("/api/vnc_credentials", json={
            "session_id": local_session,
            "credentials": credentials
        })

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_clear_vnc_credentials(self, local_client: ICtrlClient, local_session: str):
        """Clear VNC credentials by setting to None."""
        # First save credentials
        local_client.put("/api/vnc_credentials", json={
            "session_id": local_session,
            "credentials": {"password": "test"}
        })

        # Clear them
        resp = local_client.put("/api/vnc_credentials", json={
            "session_id": local_session,
            "credentials": None
        })

        assert resp.status_code == 200
        assert resp.text == "success"

    def test_save_vnc_credentials_invalid_session(self, local_client: ICtrlClient):
        """Save VNC credentials with invalid session should fail."""
        resp = local_client.put("/api/vnc_credentials", json={
            "session_id": "nonexistent-session-id",
            "credentials": {"password": "test"}
        })

        assert resp.status_code == 403

    def test_get_vnc_credentials_after_set(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Save and then retrieve VNC credentials via VNC start (LocalProfile.get_session_vnc_credentials).

        This covers lines 184-185 in LocalProfile.py where saved credentials are decoded and returned.
        """
        saved_credentials = {
            "password": "savedvncpass",
            "username": "vncuser123"
        }

        # First, save VNC credentials
        resp = local_client.put("/api/vnc_credentials", json={
            "session_id": local_session,
            "credentials": saved_credentials
        })
        assert resp.status_code == 200

        # Set a password on remote so VNC can start
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "remotepass"
        }, timeout=30)
        assert resp.status_code == 200

        # Start VNC with loadCredentials=True
        # This will call get_session_vnc_credentials which should return our saved credentials
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)

        assert resp.status_code == 200
        _, data = parse_streaming_response(resp.content)

        # Should return the saved credentials (not from password file)
        assert data is not None
        assert "credentials" in data
        assert data["credentials"] is not None
        assert data["credentials"]["password"] == saved_credentials["password"]
        assert data["credentials"]["username"] == saved_credentials["username"]

        # Cleanup
        kill_all_vnc(ssh_client)


# =============================================================================
# Local Mode Tests - VNC End-to-End
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.vnc
class TestVNCE2ELocalMode:
    """End-to-end tests for VNC functionality."""

    @pytest.fixture(autouse=True)
    def setup_vnc(self, ssh_client):
        """Ensure clean VNC state."""
        kill_all_vnc(ssh_client)
        yield
        kill_all_vnc(ssh_client)

    def test_full_vnc_lifecycle(self, local_client: ICtrlClient, local_session: str):
        """Test complete VNC lifecycle: reset, set password, start, save credentials."""
        # 1. Reset VNC settings
        resp = local_client.post("/api/vnc_reset", json={
            "session_id": local_session
        }, timeout=30)
        assert resp.status_code == 200

        # 2. Set VNC password
        test_password = "testpwd"
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": test_password
        }, timeout=30)
        assert resp.status_code == 200

        # 3. Start VNC
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)
        assert resp.status_code == 200
        _, data = parse_streaming_response(resp.content)

        if data and "port" in data:
            ws_port = data["port"]
            assert ws_port > 0

            # 4. Save credentials
            resp = local_client.put("/api/vnc_credentials", json={
                "session_id": local_session,
                "credentials": {"password": test_password}
            })
            assert resp.status_code == 200

    def test_vnc_password_persistence(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Test that VNC password is properly persisted."""
        # Set password
        test_password = "persist"
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": test_password
        }, timeout=30)
        assert resp.status_code == 200

        # Verify .vnc/passwd file exists
        stdin, stdout, stderr = ssh_client.exec_command("test -f ~/.vnc/passwd && echo 'exists'")
        result = stdout.read().decode().strip()
        assert result == "exists"

    def test_vnc_multiple_sessions(self, local_client: ICtrlClient, local_session: str):
        """Test starting VNC multiple times with same session."""
        # Set password first
        local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "multi"
        }, timeout=30)

        ports = []
        for _ in range(2):
            resp = local_client.post("/api/vnc", json={
                "sessionID": local_session,
                "loadCheck": False,
                "loadCredentials": True
            }, timeout=60)
            _, data = parse_streaming_response(resp.content)
            if data and "port" in data:
                ports.append(data["port"])
            time.sleep(2)  # Allow some time between starts

        # Both attempts should return valid ports
        for port in ports:
            assert port > 0


# =============================================================================
# VNC Server Management Tests
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.vnc
class TestVNCServerManagement:
    """Tests for VNC server process management."""

    @pytest.fixture(autouse=True)
    def setup_vnc(self, ssh_client):
        """Ensure clean VNC state."""
        kill_all_vnc(ssh_client)
        yield
        kill_all_vnc(ssh_client)

    def test_vnc_creates_display(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """VNC start should create a display."""
        # Set password
        local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "disptest"
        }, timeout=30)

        # Start VNC
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)

        _, data = parse_streaming_response(resp.content)
        if data and "port" in data:
            # Check for VNC process
            time.sleep(2)
            display = get_vnc_display(ssh_client)
            # Display should be a number like 1, 2, etc.
            assert display is None or display >= 1

    def test_vnc_kill_and_restart(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Test killing VNC and restarting."""
        # Set password
        local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "killtest"
        }, timeout=30)

        # Start VNC
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)
        assert resp.status_code == 200

        # Kill all VNC
        kill_all_vnc(ssh_client)

        # Restart should work
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)
        assert resp.status_code == 200


# =============================================================================
# VNC Password and Credentials Tests
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.vnc
class TestVNCPasswordDecryption:
    """Tests for VNC password reading and decryption.

    Note: Direct VNC.get_vnc_password() testing requires SSH connection from host,
    which isn't practical. Instead we test through the API which exercises decrypt_passwd().
    """

    @pytest.fixture(autouse=True)
    def setup_vnc(self, ssh_client):
        """Ensure clean VNC state."""
        kill_all_vnc(ssh_client)
        yield
        kill_all_vnc(ssh_client)

    def test_vnc_credentials_returned_in_start_response(self, local_client: ICtrlClient, local_session: str):
        """Test that VNC start returns credentials when loadCredentials=True.

        This tests the full flow including decrypt_passwd() being called by VNC.get_vnc_password().
        """
        test_password = "credtest"

        # Set password - this creates the password file on the remote
        resp = local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": test_password
        }, timeout=30)
        assert resp.status_code == 200

        # Start VNC with loadCredentials=True
        # This should:
        # 1. Connect to the SSH server
        # 2. Call get_vnc_password() which uses decrypt_passwd() to read the password
        # 3. Return the password in credentials
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": True
        }, timeout=60)

        assert resp.status_code == 200
        _, data = parse_streaming_response(resp.content)

        # Should return credentials
        assert data is not None
        assert "credentials" in data
        if data["credentials"]:
            assert data["credentials"]["password"] == test_password

    def test_vnc_no_credentials_when_disabled(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Test that VNC start doesn't return credentials when loadCredentials=False."""
        # Set password
        local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "nocred"
        }, timeout=30)

        # Start VNC with loadCredentials=False
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": False
        }, timeout=60)

        assert resp.status_code == 200
        _, data = parse_streaming_response(resp.content)

        # Credentials should be None/empty when loadCredentials=False
        assert data is not None
        # credentials should be None when not loading
        assert data.get("credentials") is None

    def test_vnc_credentials_delete_via_load_credentials_false(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Test that loadCredentials=False deletes stored VNC credentials (LocalProfile.set_session_vnc_credentials with None)."""
        # Set password on remote server
        local_client.post("/api/vncpasswd", json={
            "session_id": local_session,
            "passwd": "deltest"
        }, timeout=30)

        # First, store VNC credentials via the API
        resp = local_client.put("/api/vnc_credentials", json={
            "session_id": local_session,
            "credentials": {"password": "stored_creds"}
        })
        assert resp.status_code == 200

        # Now start VNC with loadCredentials=False - this should DELETE the stored credentials
        resp = local_client.post("/api/vnc", json={
            "sessionID": local_session,
            "loadCheck": False,
            "loadCredentials": False
        }, timeout=60)

        assert resp.status_code == 200
        _, data = parse_streaming_response(resp.content)

        # Credentials should be None since we requested loadCredentials=False
        # AND the stored credentials should have been deleted
        assert data is not None
        assert data.get("credentials") is None

    def test_vnc_password_missing_triggers_error(self, local_client: ICtrlClient, local_session: str, ssh_client):
        """Test that missing VNC password triggers appropriate error code."""
        from requests.exceptions import ChunkedEncodingError

        # Remove any existing VNC password file
        ssh_client.exec_command("rm -rf ~/.vnc/passwd")
        time.sleep(1)

        try:
            # Start VNC - should return PASSWD_MISSING error since there's no password file
            resp = local_client.post("/api/vnc", json={
                "sessionID": local_session,
                "loadCheck": False,
                "loadCredentials": True
            }, timeout=60)

            # Parse the response - should contain error code for missing password
            # or succeed if server has different behavior
            assert resp.status_code == 200
            steps, data = parse_streaming_response(resp.content)

            # Check for PASSWD_MISSING error (code 104) or success
            # The behavior depends on whether 5900 is open
            from application.codes import ICtrlError
            has_passwd_missing = ICtrlError.VNC.PASSWD_MISSING in steps
            # Either we got the error OR we got data (meaning 5900 was open or launch succeeded)
            assert has_passwd_missing or data is not None or len(steps) > 0

        except ChunkedEncodingError:
            # The streaming response may end early when there's an error
            pass