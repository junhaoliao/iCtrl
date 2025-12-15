"""
Unit tests for features/SFTP.py.

Tests the SFTP class methods.
"""

import sys
import stat
import pytest
from unittest.mock import patch, MagicMock, PropertyMock


def get_sftp_features_module():
    """Get the features/SFTP module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.features.SFTP']


@pytest.fixture
def mock_sftp_client():
    """Create a mock SFTP client."""
    return MagicMock()


@pytest.fixture
def mock_ssh_client():
    """Create a mock SSH client."""
    return MagicMock()


class TestSFTPInit:
    """Tests for SFTP initialization."""

    def test_sftp_init(self):
        """SFTP initializes with None sftp attribute."""
        sftp_module = get_sftp_features_module()
        sftp = sftp_module.SFTP()
        assert sftp.sftp is None


class TestSFTPConnect:
    """Tests for SFTP connect method."""

    def test_connect_success(self):
        """connect() opens SFTP session on successful SSH connection."""
        sftp_module = get_sftp_features_module()

        with patch.object(sftp_module.Connection, 'connect') as mock_super_connect:
            mock_super_connect.return_value = (True, '')

            sftp = sftp_module.SFTP()
            sftp.client = MagicMock()
            mock_sftp_client = MagicMock()
            sftp.client.open_sftp.return_value = mock_sftp_client

            status, reason = sftp.connect('host', 'user', password='pass')

            assert status is True
            assert reason == ''
            assert sftp.sftp is mock_sftp_client
            mock_sftp_client.chdir.assert_called_once_with('.')

    def test_connect_ssh_failure(self):
        """connect() returns failure if SSH connection fails."""
        sftp_module = get_sftp_features_module()

        with patch.object(sftp_module.Connection, 'connect') as mock_super_connect:
            mock_super_connect.return_value = (False, 'SSH connection failed')

            sftp = sftp_module.SFTP()
            status, reason = sftp.connect('host', 'user', password='pass')

            assert status is False
            assert reason == 'SSH connection failed'

    def test_connect_sftp_failure(self):
        """connect() returns failure if SFTP session fails to open."""
        sftp_module = get_sftp_features_module()

        with patch.object(sftp_module.Connection, 'connect') as mock_super_connect:
            mock_super_connect.return_value = (True, '')

            sftp = sftp_module.SFTP()
            sftp.client = MagicMock()
            sftp.client.open_sftp.side_effect = Exception('SFTP failed')

            status, reason = sftp.connect('host', 'user', password='pass')

            assert status is False
            assert 'SFTP failed' in reason


class TestSFTPLs:
    """Tests for SFTP ls method."""

    def test_ls_current_dir(self):
        """ls() lists files in current directory."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        sftp.sftp.getcwd.return_value = '/home/user'

        mock_attr1 = MagicMock()
        mock_attr1.filename = 'file1.txt'
        mock_attr1.st_mode = 0o100644
        mock_attr1.st_size = 100
        mock_attr1.st_atime = 1234567890
        mock_attr1.st_mtime = 1234567890

        mock_attr2 = MagicMock()
        mock_attr2.filename = 'dir1'
        mock_attr2.st_mode = 0o040755
        mock_attr2.st_size = 4096
        mock_attr2.st_atime = 1234567890
        mock_attr2.st_mtime = 1234567890

        sftp.sftp.listdir_attr.return_value = [mock_attr1, mock_attr2]

        status, cwd, file_list = sftp.ls("")

        assert status is True
        assert cwd == '/home/user'
        assert len(file_list) == 2
        assert file_list[0]['id'] == 'file1.txt'
        assert file_list[1]['id'] == 'dir1'

    def test_ls_specific_path(self):
        """ls() changes to specified directory."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        sftp.sftp.getcwd.return_value = '/home/user/subdir'
        sftp.sftp.listdir_attr.return_value = []

        status, cwd, file_list = sftp.ls("/home/user/subdir")

        sftp.sftp.chdir.assert_called_once_with('/home/user/subdir')
        assert status is True
        assert cwd == '/home/user/subdir'

    def test_ls_error(self):
        """ls() returns failure on exception."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        sftp.sftp.chdir.side_effect = Exception('No such directory')

        status, error_msg, file_list = sftp.ls("/nonexistent")

        assert status is False
        assert 'No such directory' in error_msg
        assert file_list == []


class TestSFTPRegSize:
    """Tests for SFTP reg_size method."""

    def test_reg_size_regular_file(self):
        """reg_size() returns True for regular file."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()

        mock_stat = MagicMock()
        mock_stat.st_mode = stat.S_IFREG | 0o644  # Regular file
        mock_stat.st_size = 12345
        sftp.sftp.stat.return_value = mock_stat

        is_reg, size = sftp.reg_size('file.txt')

        assert is_reg is True
        assert size == 12345

    def test_reg_size_directory(self):
        """reg_size() returns False for directory."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()

        mock_stat = MagicMock()
        mock_stat.st_mode = stat.S_IFDIR | 0o755  # Directory
        mock_stat.st_size = 4096
        sftp.sftp.stat.return_value = mock_stat

        is_reg, size = sftp.reg_size('mydir')

        assert is_reg is False
        assert size == 4096


class TestSFTPDlGenerator:
    """Tests for SFTP dl_generator method."""

    def test_dl_generator_success(self):
        """dl_generator() yields file chunks."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()

        mock_file = MagicMock()
        mock_file.read.side_effect = [b'chunk1', b'chunk2', b'']
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        sftp.sftp.file.return_value = mock_file

        chunks = list(sftp.dl_generator('file.txt'))

        assert len(chunks) == 2
        assert chunks[0] == b'chunk1'
        assert chunks[1] == b'chunk2'

    def test_dl_generator_permission_error(self):
        """dl_generator() yields empty bytes on permission error."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        sftp.sftp.file.side_effect = PermissionError('Permission denied')

        chunks = list(sftp.dl_generator('protected.txt'))

        assert len(chunks) == 1
        assert chunks[0] == b''


class TestSFTPRename:
    """Tests for SFTP rename method."""

    def test_rename_success(self):
        """rename() renames file successfully."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()

        status, reason = sftp.rename('/home/user', 'old.txt', 'new.txt')

        assert status is True
        assert reason == ''
        sftp.sftp.chdir.assert_called_once_with('/home/user')
        sftp.sftp.rename.assert_called_once_with('old.txt', 'new.txt')

    def test_rename_error(self):
        """rename() returns failure on error."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        sftp.sftp.rename.side_effect = Exception('File not found')

        status, reason = sftp.rename('/home/user', 'nonexistent.txt', 'new.txt')

        assert status is False
        assert 'File not found' in reason


class TestSFTPChmod:
    """Tests for SFTP chmod method."""

    def test_chmod_success(self):
        """chmod() changes permissions successfully."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()

        with patch.object(sftp, 'exec_command_blocking') as mock_exec:
            mock_stderr = MagicMock()
            mock_stderr.readlines.return_value = []
            mock_exec.return_value = (True, 0, [], mock_stderr)

            # mode is passed as integer that gets formatted to octal
            # 493 decimal = 755 octal
            status, reason = sftp.chmod('/home/user/file.txt', 0o755, False)

            assert status is True
            assert reason == ''
            mock_exec.assert_called_once()
            call_cmd = mock_exec.call_args[0][0]
            assert '755' in call_cmd
            assert '/home/user/file.txt' in call_cmd
            assert '-R' not in call_cmd

    def test_chmod_recursive(self):
        """chmod() applies recursive flag."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()

        with patch.object(sftp, 'exec_command_blocking') as mock_exec:
            mock_stderr = MagicMock()
            mock_stderr.readlines.return_value = []
            mock_exec.return_value = (True, 0, [], mock_stderr)

            status, reason = sftp.chmod('/home/user/dir', 0o755, True)

            assert status is True
            call_cmd = mock_exec.call_args[0][0]
            assert '-R' in call_cmd

    def test_chmod_error(self):
        """chmod() returns failure on stderr output."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()

        with patch.object(sftp, 'exec_command_blocking') as mock_exec:
            mock_stderr = MagicMock()
            mock_stderr.readlines.return_value = ['chmod: Permission denied']
            mock_exec.return_value = (True, 1, [], mock_stderr)

            status, reason = sftp.chmod('/etc/passwd', 0o777, False)

            assert status is False
            assert 'permission' in reason.lower()


class TestSFTPFile:
    """Tests for SFTP file method."""

    def test_file_creates_writable_file(self):
        """file() creates a writable pipelined file."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        mock_file = MagicMock()
        sftp.sftp.file.return_value = mock_file

        result = sftp.file('test.txt')

        sftp.sftp.file.assert_called_once_with('test.txt', mode='w')
        mock_file.set_pipelined.assert_called_once_with(True)
        assert result is mock_file


class TestSFTPRm:
    """Tests for SFTP rm method."""

    def test_rm_success(self):
        """rm() removes files successfully."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        sftp.client.exec_command.return_value = (None, None, mock_stderr)

        status, reason = sftp.rm('/home/user', ['file1.txt', 'file2.txt'])

        assert status is True
        assert reason == ''

    def test_rm_error(self):
        """rm() returns failure on stderr output."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = ['rm: cannot remove: Permission denied']
        sftp.client.exec_command.return_value = (None, None, mock_stderr)

        status, reason = sftp.rm('/home/user', ['protected.txt'])

        assert status is False
        assert 'permission' in reason.lower()

    def test_rm_many_files_batched(self):
        """rm() batches commands for many files."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        sftp.client.exec_command.return_value = (None, None, mock_stderr)

        # Create list of 60 files (more than batch size of 50)
        files = [f'file{i}.txt' for i in range(60)]
        status, reason = sftp.rm('/home/user', files)

        assert status is True
        # Should have been called at least twice (once for first 50, once for remaining)
        assert sftp.client.exec_command.call_count >= 2

    def test_rm_exactly_50_files_triggers_batch(self):
        """rm() executes batch when exactly 50 files are queued (counter == 50 branch)."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        sftp.client.exec_command.return_value = (None, None, mock_stderr)

        # Create list of exactly 50 files to trigger the counter == 50 branch
        files = [f'file{i}.txt' for i in range(50)]
        status, reason = sftp.rm('/home/user', files)

        assert status is True
        assert reason == ''
        # Should be called twice: once at counter==50, once for the final (empty) batch
        assert sftp.client.exec_command.call_count == 2

    def test_rm_100_files_triggers_two_batches(self):
        """rm() executes two full batches for 100 files."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        sftp.client.exec_command.return_value = (None, None, mock_stderr)

        # Create list of exactly 100 files to trigger counter==50 twice
        files = [f'file{i}.txt' for i in range(100)]
        status, reason = sftp.rm('/home/user', files)

        assert status is True
        # Should be called 3 times: twice at counter==50, once for the final (empty) batch
        assert sftp.client.exec_command.call_count == 3

    def test_rm_batch_error_in_first_batch(self):
        """rm() returns error when first batch (counter==50) fails."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()

        # First call returns error, second call succeeds
        mock_stderr_error = MagicMock()
        mock_stderr_error.readlines.return_value = ['rm: cannot remove: Permission denied']
        mock_stderr_success = MagicMock()
        mock_stderr_success.readlines.return_value = []
        sftp.client.exec_command.side_effect = [
            (None, None, mock_stderr_error),  # First batch (50 files) - error
            (None, None, mock_stderr_success),  # Second batch (remaining) - success
        ]

        # Create list of 60 files
        files = [f'file{i}.txt' for i in range(60)]
        status, reason = sftp.rm('/home/user', files)

        assert status is False
        assert 'permission' in reason.lower()
        assert sftp.client.exec_command.call_count == 2

    def test_rm_batch_error_in_final_batch(self):
        """rm() returns error when final batch fails (line 174 -> 175 branch)."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()

        # First call succeeds, second call (final batch) returns error
        mock_stderr_success = MagicMock()
        mock_stderr_success.readlines.return_value = []
        mock_stderr_error = MagicMock()
        mock_stderr_error.readlines.return_value = ['rm: cannot remove: Permission denied']
        sftp.client.exec_command.side_effect = [
            (None, None, mock_stderr_success),  # First batch (50 files) - success
            (None, None, mock_stderr_error),    # Final batch (remaining 10) - error
        ]

        # Create list of 60 files
        files = [f'file{i}.txt' for i in range(60)]
        status, reason = sftp.rm('/home/user', files)

        assert status is False
        assert 'permission' in reason.lower()
        assert sftp.client.exec_command.call_count == 2

    def test_rm_batch_error_in_both_batches(self):
        """rm() handles errors in both batched and final execution."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()

        # Both calls return errors
        mock_stderr_error = MagicMock()
        mock_stderr_error.readlines.return_value = ['rm: cannot remove: Permission denied']
        sftp.client.exec_command.return_value = (None, None, mock_stderr_error)

        # Create list of 60 files
        files = [f'file{i}.txt' for i in range(60)]
        status, reason = sftp.rm('/home/user', files)

        assert status is False
        assert 'permission' in reason.lower()

    def test_rm_empty_list(self):
        """rm() handles empty file list."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        sftp.client.exec_command.return_value = (None, None, mock_stderr)

        status, reason = sftp.rm('/home/user', [])

        assert status is True
        assert reason == ''
        # Should still be called once for the final batch (even if empty)
        assert sftp.client.exec_command.call_count == 1

    def test_rm_verifies_batch_command_format(self):
        """rm() constructs correct command with quoted filenames."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.client = MagicMock()
        mock_stderr = MagicMock()
        mock_stderr.readlines.return_value = []
        sftp.client.exec_command.return_value = (None, None, mock_stderr)

        files = ['file with spaces.txt', 'normal.txt']
        status, reason = sftp.rm('/home/user', files)

        assert status is True
        # Verify the command was constructed correctly
        call_args = sftp.client.exec_command.call_args[0][0]
        assert 'cd "/home/user" && rm -rf' in call_args
        assert '"file with spaces.txt"' in call_args
        assert '"normal.txt"' in call_args


class TestSFTPMkdir:
    """Tests for SFTP mkdir method."""

    def test_mkdir_success(self):
        """mkdir() creates directory successfully."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()

        with patch.object(sftp, 'exec_command_blocking') as mock_exec:
            mock_stderr = MagicMock()
            mock_stderr.readlines.return_value = []
            mock_exec.return_value = (True, 0, [], mock_stderr)

            status, reason = sftp.mkdir('/home/user', 'newdir')

            assert status is True
            assert reason == ''

    def test_mkdir_error(self):
        """mkdir() returns failure on stderr output."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()

        with patch.object(sftp, 'exec_command_blocking') as mock_exec:
            mock_stderr = MagicMock()
            mock_stderr.readlines.return_value = ['mkdir: cannot create directory: File exists']
            mock_exec.return_value = (True, 1, [], mock_stderr)

            status, reason = sftp.mkdir('/home/user', 'existingdir')

            assert status is False
            assert 'exists' in reason.lower()


class TestSFTPZipGenerator:
    """Tests for SFTP zip_generator method."""

    def test_zip_generator_creates_zipstream(self):
        """zip_generator() creates a zipstream for files."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()

        # Mock file stat for regular file
        mock_stat = MagicMock()
        mock_stat.st_mode = stat.S_IFREG | 0o644
        sftp.sftp.stat.return_value = mock_stat

        with patch.object(sftp, 'dl_generator') as mock_dl:
            mock_dl.return_value = iter([b'content'])

            result = sftp.zip_generator('/home/user', ['file.txt'])

            # Result should be a zipstream.ZipFile
            assert result is not None
            sftp.sftp.chdir.assert_called_once_with('/home/user')


class TestSFTPZipDirRecurse:
    """Tests for SFTP _zip_dir_recurse method."""

    def test_zip_dir_recurse_file(self):
        """_zip_dir_recurse() adds file to zipstream."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()

        mock_stat = MagicMock()
        mock_stat.st_mode = stat.S_IFREG | 0o644
        sftp.sftp.stat.return_value = mock_stat

        mock_zip = MagicMock()

        with patch.object(sftp, 'dl_generator') as mock_dl:
            mock_dl.return_value = iter([b'content'])

            sftp._zip_dir_recurse(mock_zip, '/home', 'file.txt')

            mock_zip.write_iter.assert_called_once()

    def test_zip_dir_recurse_directory(self):
        """_zip_dir_recurse() recursively processes directory."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()

        # First call for directory, second for file inside
        mock_stat_dir = MagicMock()
        mock_stat_dir.st_mode = stat.S_IFDIR | 0o755
        mock_stat_file = MagicMock()
        mock_stat_file.st_mode = stat.S_IFREG | 0o644
        sftp.sftp.stat.side_effect = [mock_stat_dir, mock_stat_file]
        sftp.sftp.listdir.return_value = ['subfile.txt']

        mock_zip = MagicMock()

        with patch.object(sftp, 'dl_generator') as mock_dl:
            mock_dl.return_value = iter([b'content'])

            sftp._zip_dir_recurse(mock_zip, '/home', 'mydir')

            # Should have processed both the directory and the file inside
            assert sftp.sftp.stat.call_count == 2
            mock_zip.write_iter.assert_called_once()

    def test_zip_dir_recurse_file_not_found(self):
        """_zip_dir_recurse() handles FileNotFoundError (symlinks)."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        sftp.sftp.stat.side_effect = FileNotFoundError('Broken symlink')

        mock_zip = MagicMock()

        # Should not raise
        sftp._zip_dir_recurse(mock_zip, '/home', 'brokenlink')

        # Should not write anything
        mock_zip.write_iter.assert_not_called()

    def test_zip_dir_recurse_permission_error(self):
        """_zip_dir_recurse() handles PermissionError."""
        sftp_module = get_sftp_features_module()

        sftp = sftp_module.SFTP()
        sftp.sftp = MagicMock()
        sftp.sftp.stat.side_effect = PermissionError('Access denied')

        mock_zip = MagicMock()

        # Should not raise
        sftp._zip_dir_recurse(mock_zip, '/home', 'protected')

        # Should not write anything
        mock_zip.write_iter.assert_not_called()
