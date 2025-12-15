"""
Unit tests for routes/sftp.py.

Tests the SFTP route handlers.
"""

import sys
import json
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO


def get_sftp_routes_module():
    """Get the routes/sftp module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.routes.sftp']


def get_codes_module():
    """Get the codes module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.codes']


@pytest.fixture
def app():
    """Flask app fixture."""
    from application import app as flask_app, api
    flask_app.config['TESTING'] = True
    if 'api' not in flask_app.blueprints:
        flask_app.register_blueprint(api, url_prefix='/api')
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


class TestSftpLs:
    """Tests for /api/sftp_ls endpoint."""

    def test_sftp_ls_success(self, client):
        """GET /api/sftp_ls returns directory listing."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.ls.return_value = (True, '/home/user', [
                {'name': 'file1.txt', 'size': 100, 'type': 'file'},
                {'name': 'dir1', 'size': 4096, 'type': 'directory'}
            ])
            mock_create.return_value = (mock_sftp, '')

            response = client.get(
                '/api/sftp_ls/test-session?path=/home/user',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['cwd'] == '/home/user'
            assert len(data['files']) == 2

    def test_sftp_ls_connection_failed(self, client):
        """GET /api/sftp_ls returns 403 if connection fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_create.return_value = (mock_sftp, b'connection error')

            response = client.get(
                '/api/sftp_ls/test-session?path=/home/user',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403

    def test_sftp_ls_directory_error(self, client):
        """GET /api/sftp_ls returns 400 if directory listing fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.ls.return_value = (False, 'No such directory', None)
            mock_create.return_value = (mock_sftp, '')

            response = client.get(
                '/api/sftp_ls/test-session?path=/nonexistent',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 400


class TestSftpDl:
    """Tests for /api/sftp_dl endpoint."""

    def test_sftp_dl_single_file(self, client):
        """GET /api/sftp_dl downloads a single file."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.reg_size.return_value = (True, 100)  # Regular file, 100 bytes
            mock_sftp.dl_generator.return_value = iter([b'file content'])
            mock_sftp.sftp = MagicMock()
            mock_create.return_value = (mock_sftp, '')

            files = json.dumps(['test.txt'])
            response = client.get(
                f'/api/sftp_dl/test-session?cwd=/home/user&files={files}',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.headers.get('Content-Disposition') == 'attachment; filename=test.txt'

    def test_sftp_dl_multiple_files_zip(self, client):
        """GET /api/sftp_dl downloads multiple files as zip."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.zip_generator.return_value = iter([b'zip content'])
            mock_sftp.sftp = MagicMock()
            mock_create.return_value = (mock_sftp, '')

            files = json.dumps(['file1.txt', 'file2.txt'])
            response = client.get(
                f'/api/sftp_dl/test-session?cwd=/home/user&files={files}',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.content_type == 'application/zip'

    def test_sftp_dl_directory_zip(self, client):
        """GET /api/sftp_dl downloads directory as zip."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.reg_size.return_value = (False, 0)  # Not a regular file (directory)
            mock_sftp.zip_generator.return_value = iter([b'zip content'])
            mock_sftp.sftp = MagicMock()
            mock_create.return_value = (mock_sftp, '')

            files = json.dumps(['mydir'])
            response = client.get(
                f'/api/sftp_dl/test-session?cwd=/home/user&files={files}',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.content_type == 'application/zip'

    def test_sftp_dl_connection_failed(self, client):
        """GET /api/sftp_dl returns 403 if connection fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_create.return_value = (mock_sftp, b'connection error')

            files = json.dumps(['test.txt'])
            response = client.get(
                f'/api/sftp_dl/test-session?cwd=/home/user&files={files}',
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403


class TestSftpRename:
    """Tests for /api/sftp_rename endpoint."""

    def test_sftp_rename_success(self, client):
        """PATCH /api/sftp_rename renames file successfully."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.rename.return_value = (True, '')
            mock_create.return_value = (mock_sftp, '')

            response = client.patch(
                '/api/sftp_rename/test-session',
                json={'cwd': '/home/user', 'old': 'oldname.txt', 'new': 'newname.txt'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_sftp_rename_failed(self, client):
        """PATCH /api/sftp_rename returns 400 if rename fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.rename.return_value = (False, 'File not found')
            mock_create.return_value = (mock_sftp, '')

            response = client.patch(
                '/api/sftp_rename/test-session',
                json={'cwd': '/home/user', 'old': 'nonexistent.txt', 'new': 'newname.txt'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 400

    def test_sftp_rename_connection_failed(self, client):
        """PATCH /api/sftp_rename returns 403 if connection fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_create.return_value = (mock_sftp, b'connection error')

            response = client.patch(
                '/api/sftp_rename/test-session',
                json={'cwd': '/home/user', 'old': 'old.txt', 'new': 'new.txt'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403


class TestSftpChmod:
    """Tests for /api/sftp_chmod endpoint."""

    def test_sftp_chmod_success(self, client):
        """PATCH /api/sftp_chmod changes permissions successfully."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.chmod.return_value = (True, '')
            mock_create.return_value = (mock_sftp, '')

            response = client.patch(
                '/api/sftp_chmod/test-session',
                json={'path': '/home/user/file.txt', 'mode': 755, 'recursive': False},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_sftp_chmod_recursive(self, client):
        """PATCH /api/sftp_chmod can change permissions recursively."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.chmod.return_value = (True, '')
            mock_create.return_value = (mock_sftp, '')

            response = client.patch(
                '/api/sftp_chmod/test-session',
                json={'path': '/home/user/dir', 'mode': 755, 'recursive': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            mock_sftp.chmod.assert_called_once_with('/home/user/dir', 755, True)

    def test_sftp_chmod_failed(self, client):
        """PATCH /api/sftp_chmod returns 400 if chmod fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.chmod.return_value = (False, 'Permission denied')
            mock_create.return_value = (mock_sftp, '')

            response = client.patch(
                '/api/sftp_chmod/test-session',
                json={'path': '/etc/passwd', 'mode': 777, 'recursive': False},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 400

    def test_sftp_chmod_connection_failed(self, client):
        """PATCH /api/sftp_chmod returns 403 if connection fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_create.return_value = (mock_sftp, b'connection error')

            response = client.patch(
                '/api/sftp_chmod/test-session',
                json={'path': '/home/user/file.txt', 'mode': 644, 'recursive': False},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403


class TestSftpMkdir:
    """Tests for /api/sftp_mkdir endpoint."""

    def test_sftp_mkdir_success(self, client):
        """PUT /api/sftp_mkdir creates directory successfully."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.mkdir.return_value = (True, '')
            mock_create.return_value = (mock_sftp, '')

            response = client.put(
                '/api/sftp_mkdir/test-session',
                json={'cwd': '/home/user', 'name': 'newdir'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_sftp_mkdir_failed(self, client):
        """PUT /api/sftp_mkdir returns 400 if mkdir fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.mkdir.return_value = (False, 'Directory already exists')
            mock_create.return_value = (mock_sftp, '')

            response = client.put(
                '/api/sftp_mkdir/test-session',
                json={'cwd': '/home/user', 'name': 'existingdir'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 400

    def test_sftp_mkdir_connection_failed(self, client):
        """PUT /api/sftp_mkdir returns 403 if connection fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_create.return_value = (mock_sftp, b'connection error')

            response = client.put(
                '/api/sftp_mkdir/test-session',
                json={'cwd': '/home/user', 'name': 'newdir'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403


class TestSftpUl:
    """Tests for /api/sftp_ul endpoint."""

    def test_sftp_ul_success(self, client):
        """POST /api/sftp_ul uploads file successfully."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_file = MagicMock()
            mock_sftp.file.return_value = mock_file
            mock_sftp.sftp = MagicMock()
            mock_create.return_value = (mock_sftp, '')

            response = client.post(
                '/api/sftp_ul/test-session',
                data=b'file content here',
                headers={
                    "Authorization": "Bearer test-auth-key",
                    "Cwd": "/home/user",
                    "Path": "uploaded.txt",
                    "Content-Type": "application/octet-stream"
                }
            )

            assert response.status_code == 200
            assert response.data == b'success'
            mock_sftp.file.assert_called_once_with(filename='uploaded.txt')
            mock_file.close.assert_called_once()

    def test_sftp_ul_with_subdirectory(self, client):
        """POST /api/sftp_ul creates subdirectory if needed."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_file = MagicMock()
            mock_sftp.file.return_value = mock_file
            mock_sftp.sftp = MagicMock()
            mock_create.return_value = (mock_sftp, '')

            response = client.post(
                '/api/sftp_ul/test-session',
                data=b'file content',
                headers={
                    "Authorization": "Bearer test-auth-key",
                    "Cwd": "/home/user",
                    "Path": "subdir/nested/file.txt",
                    "Content-Type": "application/octet-stream"
                }
            )

            assert response.status_code == 200
            # Should have called mkdir -p for the nested directory
            mock_sftp.exec_command_blocking.assert_called_once()

    def test_sftp_ul_connection_failed(self, client):
        """POST /api/sftp_ul returns 403 if connection fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_create.return_value = (mock_sftp, b'connection error')

            response = client.post(
                '/api/sftp_ul/test-session',
                data=b'file content',
                headers={
                    "Authorization": "Bearer test-auth-key",
                    "Cwd": "/home/user",
                    "Path": "file.txt",
                    "Content-Type": "application/octet-stream"
                }
            )

            assert response.status_code == 403


class TestSftpRm:
    """Tests for /api/sftp_rm endpoint."""

    def test_sftp_rm_success(self, client):
        """POST /api/sftp_rm removes files successfully."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.rm.return_value = (True, '')
            mock_create.return_value = (mock_sftp, '')

            response = client.post(
                '/api/sftp_rm/test-session',
                json={'cwd': '/home/user', 'files': ['file1.txt', 'file2.txt']},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'

    def test_sftp_rm_failed(self, client):
        """POST /api/sftp_rm returns 400 if removal fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_sftp.rm.return_value = (False, 'File not found')
            mock_create.return_value = (mock_sftp, '')

            response = client.post(
                '/api/sftp_rm/test-session',
                json={'cwd': '/home/user', 'files': ['nonexistent.txt']},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 400

    def test_sftp_rm_connection_failed(self, client):
        """POST /api/sftp_rm returns 403 if connection fails."""
        sftp_routes = get_sftp_routes_module()

        with patch.object(sftp_routes, 'create_connection') as mock_create:
            mock_sftp = MagicMock()
            mock_create.return_value = (mock_sftp, b'connection error')

            response = client.post(
                '/api/sftp_rm/test-session',
                json={'cwd': '/home/user', 'files': ['file.txt']},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
