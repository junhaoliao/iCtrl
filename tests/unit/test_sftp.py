"""
Unit tests for application/features/SFTP.py

These tests use mocking to avoid actual network connections.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import stat


class TestSFTPInit:
    """Tests for SFTP initialization."""

    @pytest.mark.unit
    def test_sftp_inherits_connection(self):
        """SFTP should inherit from Connection."""
        with patch('application.features.Connection.paramiko'):
            from application.features.SFTP import SFTP
            sftp = SFTP()

            assert hasattr(sftp, 'client')
            assert hasattr(sftp, 'sftp')

    @pytest.mark.unit
    def test_sftp_initial_state(self):
        """SFTP should have None sftp initially."""
        with patch('application.features.Connection.paramiko'):
            from application.features.SFTP import SFTP
            sftp = SFTP()

            assert sftp.sftp is None


class TestSFTPConnect:
    """Tests for SFTP.connect method."""

    @pytest.mark.unit
    def test_connect_opens_sftp_session(self):
        """connect should open SFTP session after SSH connection."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            status, reason = sftp.connect("test.host.com", "testuser", password="testpass")

            assert status is True
            assert sftp.sftp is mock_sftp
            mock_client.open_sftp.assert_called_once()

    @pytest.mark.unit
    def test_connect_failure_returns_error(self):
        """connect should return error on SSH failure."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_client.connect.side_effect = Exception("Connection refused")
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            status, reason = sftp.connect("test.host.com", "testuser", password="testpass")

            assert status is False
            assert "Connection refused" in reason


class TestSFTPLs:
    """Tests for SFTP.ls method."""

    @pytest.mark.unit
    def test_ls_returns_entries(self):
        """ls should return directory entries with attributes."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()

            # Create mock file attributes
            mock_attr1 = Mock()
            mock_attr1.filename = "file1.txt"
            mock_attr1.st_size = 1024
            mock_attr1.st_mtime = 1704067200
            mock_attr1.st_atime = 1704067200
            mock_attr1.st_mode = stat.S_IFREG | 0o644  # Regular file

            mock_attr2 = Mock()
            mock_attr2.filename = "dir1"
            mock_attr2.st_size = 4096
            mock_attr2.st_mtime = 1704067200
            mock_attr2.st_atime = 1704067200
            mock_attr2.st_mode = stat.S_IFDIR | 0o755  # Directory

            mock_sftp.listdir_attr.return_value = [mock_attr1, mock_attr2]
            mock_sftp.getcwd.return_value = "/home/testuser"
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            sftp.connect("test.host.com", "testuser", password="testpass")

            status, cwd, entries = sftp.ls("/home/testuser")

            assert status is True
            assert cwd == "/home/testuser"
            assert len(entries) == 2
            assert entries[0]['id'] == "file1.txt"
            assert entries[1]['id'] == "dir1"


class TestSFTPFileOperations:
    """Tests for SFTP file operations."""

    @pytest.mark.unit
    def test_mkdir_creates_directory(self):
        """mkdir should create a directory."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()
            mock_stderr.readlines.return_value = []
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_client.exec_command.return_value = (Mock(), mock_stdout, mock_stderr)
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            sftp.connect("test.host.com", "testuser", password="testpass")

            status, reason = sftp.mkdir("/home/testuser", "newdir")

            assert status is True

    @pytest.mark.unit
    def test_rm_deletes_files(self):
        """rm should delete files."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()
            mock_stderr = Mock()
            mock_stderr.readlines.return_value = []
            mock_client.exec_command.return_value = (Mock(), Mock(), mock_stderr)
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            sftp.connect("test.host.com", "testuser", password="testpass")

            status, reason = sftp.rm("/home/testuser", ["file.txt"])

            assert status is True

    @pytest.mark.unit
    def test_rename_moves_file(self):
        """rename should rename/move a file."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            sftp.connect("test.host.com", "testuser", password="testpass")

            status, reason = sftp.rename("/home/testuser", "old.txt", "new.txt")

            assert status is True
            mock_sftp.rename.assert_called_with("old.txt", "new.txt")

    @pytest.mark.unit
    def test_chmod_changes_permissions(self):
        """chmod should change file permissions."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()
            mock_stderr.readlines.return_value = []
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_client.exec_command.return_value = (Mock(), mock_stdout, mock_stderr)
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            sftp.connect("test.host.com", "testuser", password="testpass")

            status, reason = sftp.chmod("/home/testuser/script.sh", 755, False)

            assert status is True


class TestSFTPRegSize:
    """Tests for SFTP.reg_size method."""

    @pytest.mark.unit
    def test_reg_size_for_regular_file(self):
        """reg_size should return True and size for regular files."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()
            mock_stat = Mock()
            mock_stat.st_mode = stat.S_IFREG | 0o644
            mock_stat.st_size = 1024
            mock_sftp.stat.return_value = mock_stat
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            sftp.connect("test.host.com", "testuser", password="testpass")

            is_reg, size = sftp.reg_size("/home/testuser/file.txt")

            assert is_reg is True
            assert size == 1024

    @pytest.mark.unit
    def test_reg_size_for_directory(self):
        """reg_size should return False for directories."""
        with patch('application.features.Connection.paramiko') as mock_paramiko:
            mock_client = Mock()
            mock_sftp = Mock()
            mock_stat = Mock()
            mock_stat.st_mode = stat.S_IFDIR | 0o755
            mock_stat.st_size = 4096
            mock_sftp.stat.return_value = mock_stat
            mock_client.open_sftp.return_value = mock_sftp
            mock_paramiko.SSHClient.return_value = mock_client
            mock_paramiko.AutoAddPolicy.return_value = Mock()

            from application.features.SFTP import SFTP
            sftp = SFTP()
            sftp.connect("test.host.com", "testuser", password="testpass")

            is_reg, size = sftp.reg_size("/home/testuser/mydir")

            assert is_reg is False
