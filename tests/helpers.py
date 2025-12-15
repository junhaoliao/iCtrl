"""
Test helper functions and utilities.
"""

import ssl
import json
import struct
import threading
import time
from typing import Optional, Tuple, List, Generator
from contextlib import contextmanager

import websocket


# =============================================================================
# Response Parsing Helpers
# =============================================================================

def parse_streaming_response(content: bytes) -> Tuple[List[int], Optional[dict]]:
    """
    Parse a streaming response from terminal/VNC endpoints.

    The response format is: [step_bytes...][JSON_payload]
    Step bytes are:
    - 0-31: Progress step codes (SSH_AUTH=0, CHECK_LOAD=1, etc.)
    - 100+: Error codes (OVER_LOADED=204, PASSWD_MISSING=121, etc.)
    The JSON payload starts with '{' (0x7b).

    Returns:
        Tuple of (step_codes, final_json_payload)
    """
    steps = []
    json_data = None

    i = 0
    while i < len(content):
        byte_val = content[i]

        # JSON starts with '{'
        if byte_val == ord('{'):
            # Start of JSON payload
            try:
                json_str = content[i:].decode('utf-8')
                json_data = json.loads(json_str)
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not valid JSON, treat as step code
                steps.append(byte_val)
                i += 1
        elif byte_val < 32 or byte_val >= 100:
            # Valid step code (0-31) or error code (100+)
            steps.append(byte_val)
            i += 1
        else:
            # Unexpected byte in 32-99 range, skip
            i += 1

    return steps, json_data


def parse_step_codes(content: bytes) -> List[int]:
    """Extract just the step codes from streaming response."""
    steps, _ = parse_streaming_response(content)
    return steps


# =============================================================================
# WebSocket Helpers
# =============================================================================

class TerminalWebSocket:
    """Helper for terminal WebSocket testing."""

    def __init__(self, url: str, auth_key: Optional[str] = None):
        self.url = url
        self.auth_key = auth_key
        self.ws: Optional[websocket.WebSocket] = None
        self.received_data: List[bytes] = []
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_flag = False

    def connect(self, timeout: float = 10.0):
        """Connect to WebSocket."""
        headers = {}
        if self.auth_key:
            headers["Authorization"] = f"Bearer {self.auth_key}"

        self.ws = websocket.create_connection(
            self.url,
            header=headers,
            sslopt={"cert_reqs": ssl.CERT_NONE},
            timeout=timeout
        )

        # Start reader thread
        self._stop_flag = False
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def _read_loop(self):
        """Background thread to read WebSocket messages."""
        while not self._stop_flag and self.ws:
            try:
                data = self.ws.recv()
                if isinstance(data, str):
                    data = data.encode()
                self.received_data.append(data)
            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                break

    def send(self, data: str | bytes):
        """Send data to terminal."""
        if isinstance(data, str):
            data = data.encode()
        self.ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)

    def recv_all(self, timeout: float = 2.0) -> bytes:
        """Get all received data, waiting until data arrives or timeout."""
        start = time.time()
        # Wait until we have data or timeout
        while time.time() - start < timeout:
            if self.received_data:
                # Give a little more time for additional data to arrive
                time.sleep(0.1)
                break
            time.sleep(0.05)
        return b"".join(self.received_data)

    def wait_for_data(self, contains: bytes, timeout: float = 3.0) -> bool:
        """Wait until received data contains the expected bytes."""
        start = time.time()
        while time.time() - start < timeout:
            data = b"".join(self.received_data)
            if contains in data:
                return True
            time.sleep(0.05)
        return False

    def close(self):
        """Close WebSocket connection."""
        self._stop_flag = True
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        if self._reader_thread:
            self._reader_thread.join(timeout=1.0)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AudioWebSocket:
    """Helper for audio WebSocket testing."""

    def __init__(self, url: str, auth_key: Optional[str] = None):
        self.url = url
        self.auth_key = auth_key
        self.ws: Optional[websocket.WebSocket] = None
        self.received_chunks: List[bytes] = []
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_flag = False

    def connect(self, timeout: float = 15.0):
        """Connect to WebSocket."""
        headers = {}
        if self.auth_key:
            headers["Authorization"] = f"Bearer {self.auth_key}"

        self.ws = websocket.create_connection(
            self.url,
            header=headers,
            sslopt={"cert_reqs": ssl.CERT_NONE},
            timeout=timeout
        )

        # Start reader thread
        self._stop_flag = False
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def _read_loop(self):
        """Background thread to read audio data."""
        while not self._stop_flag and self.ws:
            try:
                data = self.ws.recv()
                if isinstance(data, bytes):
                    self.received_chunks.append(data)
            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                break

    def wait_for_audio(self, min_chunks: int = 1, timeout: float = 15.0) -> bool:
        """Wait for audio data to arrive."""
        start = time.time()
        while time.time() - start < timeout:
            if len(self.received_chunks) >= min_chunks:
                return True
            time.sleep(0.5)
        return False

    def close(self):
        """Close WebSocket connection."""
        self._stop_flag = True
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        if self._reader_thread:
            self._reader_thread.join(timeout=1.0)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# =============================================================================
# SFTP Testing Helpers
# =============================================================================

def create_test_file(ssh_client, path: str, content: str = "test content"):
    """Create a test file on remote server."""
    stdin, stdout, stderr = ssh_client.exec_command(f'echo "{content}" > {path}')
    stdout.channel.recv_exit_status()


def create_test_directory(ssh_client, path: str):
    """Create a test directory on remote server."""
    stdin, stdout, stderr = ssh_client.exec_command(f'mkdir -p {path}')
    stdout.channel.recv_exit_status()


def cleanup_test_path(ssh_client, path: str):
    """Remove test file/directory on remote server."""
    stdin, stdout, stderr = ssh_client.exec_command(f'rm -rf {path}')
    stdout.channel.recv_exit_status()


def get_file_content(ssh_client, path: str) -> str:
    """Get file content from remote server."""
    stdin, stdout, stderr = ssh_client.exec_command(f'cat {path}')
    return stdout.read().decode().strip()


def file_exists(ssh_client, path: str) -> bool:
    """Check if file exists on remote server."""
    stdin, stdout, stderr = ssh_client.exec_command(f'test -e {path} && echo "exists"')
    return stdout.read().decode().strip() == "exists"


# =============================================================================
# VNC Testing Helpers
# =============================================================================

def get_vnc_display(ssh_client) -> Optional[int]:
    """Get current VNC display number."""
    stdin, stdout, stderr = ssh_client.exec_command('vncserver -list')
    output = stdout.read().decode()

    import re
    match = re.search(r':(\d+)', output)
    if match:
        return int(match.group(1))
    return None


def kill_all_vnc(ssh_client):
    """Kill all VNC servers for test user."""
    ssh_client.exec_command('vncserver -kill ":*" 2>/dev/null || true')
    ssh_client.exec_command('killall -q Xtigervnc 2>/dev/null || true')
    time.sleep(0.5)


# =============================================================================
# Assertion Helpers
# =============================================================================

def assert_json_response(response, expected_keys: List[str]):
    """Assert response is JSON with expected keys."""
    assert response.headers.get("Content-Type", "").startswith("application/json")
    data = response.json()
    for key in expected_keys:
        assert key in data, f"Expected key '{key}' not in response"
    return data


def assert_success_response(response):
    """Assert response indicates success."""
    assert response.status_code == 200
    assert response.text in ("success", "logged in", "logged out", "sent")


def assert_error_response(response, status_code: int, error_contains: Optional[str] = None):
    """Assert response is an error with expected status."""
    assert response.status_code == status_code
    if error_contains:
        assert error_contains in response.text


# =============================================================================
# Context Managers
# =============================================================================

@contextmanager
def temp_remote_file(ssh_client, path: str, content: str = "test"):
    """Context manager for temporary remote file."""
    create_test_file(ssh_client, path, content)
    try:
        yield path
    finally:
        cleanup_test_path(ssh_client, path)


@contextmanager
def temp_remote_dir(ssh_client, path: str):
    """Context manager for temporary remote directory."""
    create_test_directory(ssh_client, path)
    try:
        yield path
    finally:
        cleanup_test_path(ssh_client, path)
