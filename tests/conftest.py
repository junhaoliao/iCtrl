"""
Pytest configuration and fixtures for iCtrl integration tests.

Test Environment:
- SSH Target: localhost:20022 (user: testuser, pass: TestPass123!)
- PostgreSQL: localhost:25432 (user: postgres, pass: testpassword, db: ictrl_test)
- Mailpit: SMTP SSL localhost:21465, Web UI localhost:21080
- iCtrl Local Mode: localhost:25000 (auth: test-auth-key-12345)
- iCtrl DB Mode: localhost:25001 (session-based auth)
"""

# IMPORTANT: Set up sys.argv BEFORE any application imports to prevent
# ValueError in application/__init__.py which parses sys.argv at import time
import sys
if len(sys.argv) < 2 or not sys.argv[1].isdigit():
    # Prepend default args for testing - the application expects: port, auth_key
    sys.argv = ['pytest', '5000', 'test-auth-key']

import os
import time
import pytest
import requests
import paramiko
from typing import Generator, Optional
from dataclasses import dataclass
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# =============================================================================
# Test Configuration
# =============================================================================

@dataclass
class TestConfig:
    """Test environment configuration."""
    # SSH Target (for direct paramiko access from host)
    ssh_host: str = "localhost"
    ssh_port: int = 20022
    ssh_user: str = "testuser"
    ssh_password: str = "TestPass123!"
    vnc_password: str = "testpass"

    # SSH Target for iCtrl server (Docker network hostname)
    # The iCtrl server runs in Docker and needs to reach ssh-target via Docker network
    # Note: iCtrl expects host without port - paramiko uses port 22 by default
    ssh_internal_host: str = "ssh-target"

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 25432
    db_user: str = "postgres"
    db_password: str = "testpassword"
    db_name: str = "ictrl_test"

    # MailCatcher
    mail_smtp_host: str = "localhost"
    mail_smtp_port: int = 21025
    mail_web_port: int = 21080

    # iCtrl Servers
    ictrl_local_host: str = "localhost"
    ictrl_local_port: int = 25000
    ictrl_local_auth_key: str = "test-auth-key-12345"

    ictrl_db_host: str = "localhost"
    ictrl_db_port: int = 25001

    @property
    def ictrl_local_url(self) -> str:
        return f"https://{self.ictrl_local_host}:{self.ictrl_local_port}"

    @property
    def ictrl_db_url(self) -> str:
        return f"https://{self.ictrl_db_host}:{self.ictrl_db_port}"

    @property
    def db_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


@pytest.fixture(scope="session")
def config() -> TestConfig:
    """Provide test configuration."""
    return TestConfig()


# =============================================================================
# Service Health Checks
# =============================================================================

def wait_for_service(check_fn, timeout: int = 60, interval: float = 1.0) -> bool:
    """Wait for a service to become available."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            if check_fn():
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False


@pytest.fixture(scope="session")
def ensure_ssh_target(config: TestConfig) -> bool:
    """Ensure SSH target is available."""
    def check():
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                config.ssh_host,
                port=config.ssh_port,
                username=config.ssh_user,
                password=config.ssh_password,
                timeout=5
            )
            client.close()
            return True
        except Exception:
            return False

    if not wait_for_service(check, timeout=60):
        pytest.skip("SSH target not available")
    return True


@pytest.fixture(scope="session")
def ensure_postgres(config: TestConfig) -> bool:
    """Ensure PostgreSQL is available."""
    import psycopg2

    def check():
        try:
            conn = psycopg2.connect(
                host=config.db_host,
                port=config.db_port,
                user=config.db_user,
                password=config.db_password,
                dbname=config.db_name
            )
            conn.close()
            return True
        except Exception:
            return False

    if not wait_for_service(check, timeout=60):
        pytest.skip("PostgreSQL not available")
    return True


@pytest.fixture(scope="session")
def ensure_ictrl_local(config: TestConfig) -> bool:
    """Ensure iCtrl local mode server is available."""
    def check():
        try:
            resp = requests.get(
                f"{config.ictrl_local_url}/api/userid",
                headers={"Authorization": f"Bearer {config.ictrl_local_auth_key}"},
                verify=False,
                timeout=5
            )
            return resp.status_code == 200
        except Exception:
            return False

    if not wait_for_service(check, timeout=90):
        pytest.skip("iCtrl local server not available")
    return True


@pytest.fixture(scope="session")
def ensure_ictrl_db(config: TestConfig, ensure_postgres) -> bool:
    """Ensure iCtrl database mode server is available."""
    def check():
        try:
            # DB mode requires login, so just check if server responds
            resp = requests.get(
                f"{config.ictrl_db_url}/api/userid",
                verify=False,
                timeout=5
            )
            # 403 is expected when not logged in
            return resp.status_code in (200, 403)
        except Exception:
            return False

    if not wait_for_service(check, timeout=90):
        pytest.skip("iCtrl DB server not available")
    return True


# =============================================================================
# HTTP Client Fixtures
# =============================================================================

class ICtrlClient:
    """HTTP client for iCtrl API with authentication."""

    def __init__(self, base_url: str, auth_key: Optional[str] = None):
        self.base_url = base_url
        self.auth_key = auth_key
        self.session = requests.Session()
        self.session.verify = False  # Self-signed certs

        if auth_key:
            self.session.headers["Authorization"] = f"Bearer {auth_key}"

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    def patch(self, path: str, **kwargs) -> requests.Response:
        return self.session.patch(f"{self.base_url}{path}", **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.session.put(f"{self.base_url}{path}", **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.session.delete(f"{self.base_url}{path}", **kwargs)


@pytest.fixture(scope="function")
def local_client(config: TestConfig, ensure_ictrl_local) -> Generator[ICtrlClient, None, None]:
    """HTTP client for iCtrl in local mode."""
    client = ICtrlClient(config.ictrl_local_url, config.ictrl_local_auth_key)
    yield client
    client.session.close()


@pytest.fixture(scope="function")
def db_client(config: TestConfig, ensure_ictrl_db) -> Generator[ICtrlClient, None, None]:
    """HTTP client for iCtrl in database mode (not logged in)."""
    client = ICtrlClient(config.ictrl_db_url)
    yield client
    client.session.close()


# =============================================================================
# SSH Client Fixture
# =============================================================================

@pytest.fixture(scope="function")
def ssh_client(config: TestConfig, ensure_ssh_target) -> Generator[paramiko.SSHClient, None, None]:
    """Paramiko SSH client connected to test target."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        config.ssh_host,
        port=config.ssh_port,
        username=config.ssh_user,
        password=config.ssh_password
    )
    yield client
    client.close()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def clean_db(config: TestConfig, ensure_postgres):
    """Clean database before each test."""
    import psycopg2

    conn = psycopg2.connect(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        dbname=config.db_name
    )
    cur = conn.cursor()

    # Truncate tables in correct order (respecting foreign keys)
    cur.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ictrl') THEN
                TRUNCATE TABLE ictrl.vnc_credentials CASCADE;
                TRUNCATE TABLE ictrl.session CASCADE;
                TRUNCATE TABLE ictrl.user CASCADE;
            END IF;
        END $$;
    """)

    conn.commit()
    cur.close()
    conn.close()

    yield


# =============================================================================
# Mail Fixtures (Mailpit API v1)
# =============================================================================

@pytest.fixture(scope="function")
def clear_mailbox(config: TestConfig):
    """Clear all emails in Mailpit."""
    try:
        requests.delete(f"http://{config.mail_smtp_host}:{config.mail_web_port}/api/v1/messages")
    except Exception:
        pass  # Mailpit might not be running
    yield


def get_emails(config: TestConfig) -> list:
    """Get all emails from Mailpit."""
    try:
        resp = requests.get(f"http://{config.mail_smtp_host}:{config.mail_web_port}/api/v1/messages")
        data = resp.json()
        return data.get("messages", [])
    except Exception:
        return []


# =============================================================================
# Test Data Generators
# =============================================================================

@pytest.fixture
def unique_username() -> str:
    """Generate unique username for tests."""
    import uuid
    return f"testuser_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def valid_password() -> str:
    """Valid password meeting all requirements."""
    return "TestPass123!"


@pytest.fixture
def valid_email(unique_username: str) -> str:
    """Valid email for tests (must end with utoronto.ca)."""
    return f"{unique_username}@mail.utoronto.ca"


# =============================================================================
# Session Fixtures for Local Mode
# =============================================================================

@pytest.fixture(scope="function")
def local_session(local_client: ICtrlClient, config: TestConfig) -> Generator[str, None, None]:
    """Create a test SSH session in local mode and return session_id."""
    # Create session using internal Docker network hostname
    # The iCtrl server runs in Docker and needs to connect to ssh-target via Docker network
    # Note: iCtrl expects host without port - paramiko uses port 22 by default
    resp = local_client.post("/api/session", json={
        "host": config.ssh_internal_host,
        "username": config.ssh_user,
        "password": config.ssh_password
    })

    if resp.status_code != 200:
        pytest.skip(f"Could not create session: {resp.text}")

    # Get the session ID from profiles
    resp = local_client.get("/api/profiles")
    profiles = resp.json()
    session_ids = list(profiles.get("sessions", {}).keys())

    if not session_ids:
        pytest.skip("No sessions found after creation")

    session_id = session_ids[-1]  # Get the most recently created

    yield session_id

    # Cleanup
    try:
        local_client.delete(f"/api/session?session_id={session_id}")
    except Exception:
        pass


# =============================================================================
# Markers for conditional test execution
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    pass  # Markers are defined in pyproject.toml


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on available services."""
    # Skip tests if Docker services aren't available
    # This allows running unit tests without Docker

    # Check if we should skip integration tests
    skip_integration = pytest.mark.skip(reason="Integration tests disabled")

    for item in items:
        if "integration" in item.keywords:
            # Check if Docker services are available
            if os.environ.get("SKIP_INTEGRATION_TESTS"):
                item.add_marker(skip_integration)
