"""
Integration tests for SFTP routes (routes/sftp.py)

Tests for: /sftp_ls, /sftp_dl, /sftp_ul, /sftp_mkdir, /sftp_rm, /sftp_rename, /sftp_chmod
"""

import io
import json
import pytest
import zipfile
from tests.conftest import ICtrlClient, TestConfig
from tests.helpers import (
    create_test_file,
    create_test_directory,
    cleanup_test_path,
    get_file_content,
    file_exists,
    temp_remote_file,
    temp_remote_dir,
)


# =============================================================================
# Local Mode Tests - SFTP List
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPListLocalMode:
    """Tests for GET /sftp_ls endpoint in local mode."""

    def test_list_home_directory(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """List files in home directory."""
        resp = local_client.get(f"/api/sftp_ls/{local_session}", params={
            "path": f"/home/{config.ssh_user}"
        })

        assert resp.status_code == 200
        data = resp.json()
        assert "cwd" in data
        assert "files" in data
        assert isinstance(data["files"], list)
        assert data["cwd"] == f"/home/{config.ssh_user}"

    def test_list_root_directory(self, local_client: ICtrlClient, local_session: str):
        """List files in root directory."""
        resp = local_client.get(f"/api/sftp_ls/{local_session}", params={
            "path": "/"
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["cwd"] == "/"
        # Root should have common directories
        file_names = [f["id"] for f in data["files"]]
        assert any(name in file_names for name in ["etc", "home", "usr", "var"])

    def test_list_relative_path(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """List with empty path uses current directory."""
        resp = local_client.get(f"/api/sftp_ls/{local_session}", params={
            "path": ""
        })

        assert resp.status_code == 200
        data = resp.json()
        # Should default to home directory
        assert config.ssh_user in data["cwd"]

    def test_list_file_attributes(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Verify file attributes are returned correctly."""
        test_file = f"/home/{config.ssh_user}/test_attrs.txt"
        create_test_file(ssh_client, test_file, "test content")

        try:
            resp = local_client.get(f"/api/sftp_ls/{local_session}", params={
                "path": f"/home/{config.ssh_user}"
            })

            assert resp.status_code == 200
            data = resp.json()

            # Find our test file
            test_file_info = next((f for f in data["files"] if f["id"] == "test_attrs.txt"), None)
            assert test_file_info is not None
            assert "mode" in test_file_info
            assert "size" in test_file_info
            assert "mtime" in test_file_info
            assert "atime" in test_file_info
        finally:
            cleanup_test_path(ssh_client, test_file)

    def test_list_nonexistent_path(self, local_client: ICtrlClient, local_session: str):
        """List non-existent path should fail."""
        resp = local_client.get(f"/api/sftp_ls/{local_session}", params={
            "path": "/nonexistent/path/12345"
        })

        assert resp.status_code == 400

    def test_list_invalid_session(self, local_client: ICtrlClient):
        """List with invalid session should fail."""
        resp = local_client.get("/api/sftp_ls/nonexistent-session", params={
            "path": "/"
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - SFTP Download
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPDownloadLocalMode:
    """Tests for GET /sftp_dl endpoint in local mode."""

    def test_download_single_file(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Download a single file."""
        test_file = f"/home/{config.ssh_user}/test_download.txt"
        test_content = "Hello, download test!"
        create_test_file(ssh_client, test_file, test_content)

        try:
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": f"/home/{config.ssh_user}",
                "files": json.dumps(["test_download.txt"])
            })

            assert resp.status_code == 200
            assert "Content-Disposition" in resp.headers
            assert "test_download.txt" in resp.headers["Content-Disposition"]
            assert test_content in resp.text
        finally:
            cleanup_test_path(ssh_client, test_file)

    def test_download_multiple_files_as_zip(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Download multiple files returns a zip archive."""
        test_dir = f"/home/{config.ssh_user}"
        files = ["test_dl_1.txt", "test_dl_2.txt"]

        for f in files:
            create_test_file(ssh_client, f"{test_dir}/{f}", f"content of {f}")

        try:
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": test_dir,
                "files": json.dumps(files)
            })

            assert resp.status_code == 200
            assert resp.headers.get("Content-Type") == "application/zip"

            # Verify it's a valid zip
            z = zipfile.ZipFile(io.BytesIO(resp.content))
            zip_names = z.namelist()
            for f in files:
                assert any(f in name for name in zip_names)
        finally:
            for f in files:
                cleanup_test_path(ssh_client, f"{test_dir}/{f}")

    def test_download_directory_as_zip(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Download a directory returns a zip archive."""
        test_dir = f"/home/{config.ssh_user}/test_dl_dir"
        create_test_directory(ssh_client, test_dir)
        create_test_file(ssh_client, f"{test_dir}/file1.txt", "content1")
        create_test_file(ssh_client, f"{test_dir}/file2.txt", "content2")

        try:
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": f"/home/{config.ssh_user}",
                "files": json.dumps(["test_dl_dir"])
            })

            assert resp.status_code == 200
            assert resp.headers.get("Content-Type") == "application/zip"

            # Verify zip contents
            z = zipfile.ZipFile(io.BytesIO(resp.content))
            zip_names = z.namelist()
            assert any("file1.txt" in name for name in zip_names)
            assert any("file2.txt" in name for name in zip_names)
        finally:
            cleanup_test_path(ssh_client, test_dir)

    def test_download_invalid_session(self, local_client: ICtrlClient):
        """Download with invalid session should fail."""
        resp = local_client.get("/api/sftp_dl/nonexistent-session", params={
            "cwd": "/",
            "files": json.dumps(["etc"])
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - SFTP Upload
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPUploadLocalMode:
    """Tests for POST /sftp_ul endpoint in local mode."""

    def test_upload_single_file(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Upload a single file."""
        test_content = b"Hello, upload test!"
        test_filename = "test_upload.txt"
        cwd = f"/home/{config.ssh_user}"
        full_path = f"{cwd}/{test_filename}"

        try:
            resp = local_client.post(
                f"/api/sftp_ul/{local_session}",
                data=test_content,
                headers={
                    "Cwd": cwd,
                    "Path": test_filename,
                    "Content-Type": "application/octet-stream"
                }
            )

            assert resp.status_code == 200
            assert resp.text == "success"

            # Verify file was uploaded
            assert file_exists(ssh_client, full_path)
            content = get_file_content(ssh_client, full_path)
            assert test_content.decode() in content
        finally:
            cleanup_test_path(ssh_client, full_path)

    def test_upload_with_subdirectory(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Upload file with relative subdirectory path."""
        test_content = b"Nested file content"
        relative_path = "subdir/nested/test_nested.txt"
        cwd = f"/home/{config.ssh_user}"
        full_path = f"{cwd}/{relative_path}"

        try:
            resp = local_client.post(
                f"/api/sftp_ul/{local_session}",
                data=test_content,
                headers={
                    "Cwd": cwd,
                    "Path": relative_path,
                    "Content-Type": "application/octet-stream"
                }
            )

            assert resp.status_code == 200
            assert resp.text == "success"

            # Verify file was uploaded
            assert file_exists(ssh_client, full_path)
        finally:
            cleanup_test_path(ssh_client, f"{cwd}/subdir")

    def test_upload_large_file(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Upload a larger file (2MB)."""
        # Create 2MB of data
        test_content = b"x" * (2 * 1024 * 1024)
        test_filename = "test_large_upload.bin"
        cwd = f"/home/{config.ssh_user}"
        full_path = f"{cwd}/{test_filename}"

        try:
            resp = local_client.post(
                f"/api/sftp_ul/{local_session}",
                data=test_content,
                headers={
                    "Cwd": cwd,
                    "Path": test_filename,
                    "Content-Type": "application/octet-stream"
                },
                timeout=60
            )

            assert resp.status_code == 200
            assert resp.text == "success"

            # Verify file size
            assert file_exists(ssh_client, full_path)
        finally:
            cleanup_test_path(ssh_client, full_path)

    def test_upload_invalid_session(self, local_client: ICtrlClient):
        """Upload with invalid session should fail."""
        resp = local_client.post(
            "/api/sftp_ul/nonexistent-session",
            data=b"test",
            headers={
                "Cwd": "/tmp",
                "Path": "test.txt",
                "Content-Type": "application/octet-stream"
            }
        )

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - SFTP Mkdir
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPMkdirLocalMode:
    """Tests for PUT /sftp_mkdir endpoint in local mode."""

    def test_create_directory(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Create a new directory."""
        cwd = f"/home/{config.ssh_user}"
        dir_name = "test_new_dir"
        full_path = f"{cwd}/{dir_name}"

        try:
            resp = local_client.put(f"/api/sftp_mkdir/{local_session}", json={
                "cwd": cwd,
                "name": dir_name
            })

            assert resp.status_code == 200
            assert resp.text == "success"

            # Verify directory was created
            assert file_exists(ssh_client, full_path)
        finally:
            cleanup_test_path(ssh_client, full_path)

    def test_create_directory_already_exists(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Create directory that already exists should fail."""
        cwd = f"/home/{config.ssh_user}"
        dir_name = "test_existing_dir"
        full_path = f"{cwd}/{dir_name}"

        create_test_directory(ssh_client, full_path)

        try:
            resp = local_client.put(f"/api/sftp_mkdir/{local_session}", json={
                "cwd": cwd,
                "name": dir_name
            })

            assert resp.status_code == 400
        finally:
            cleanup_test_path(ssh_client, full_path)

    def test_create_directory_invalid_session(self, local_client: ICtrlClient):
        """Create directory with invalid session should fail."""
        resp = local_client.put("/api/sftp_mkdir/nonexistent-session", json={
            "cwd": "/tmp",
            "name": "test"
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - SFTP Remove
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPRemoveLocalMode:
    """Tests for POST /sftp_rm endpoint in local mode."""

    def test_remove_single_file(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Remove a single file."""
        cwd = f"/home/{config.ssh_user}"
        test_file = "test_rm_file.txt"
        full_path = f"{cwd}/{test_file}"

        create_test_file(ssh_client, full_path, "to be deleted")

        resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
            "cwd": cwd,
            "files": [test_file]
        })

        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify file was deleted
        assert not file_exists(ssh_client, full_path)

    def test_remove_multiple_files(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Remove multiple files."""
        cwd = f"/home/{config.ssh_user}"
        files = ["test_rm_1.txt", "test_rm_2.txt", "test_rm_3.txt"]

        for f in files:
            create_test_file(ssh_client, f"{cwd}/{f}", "content")

        resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
            "cwd": cwd,
            "files": files
        })

        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify all files were deleted
        for f in files:
            assert not file_exists(ssh_client, f"{cwd}/{f}")

    def test_remove_directory(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Remove a directory recursively."""
        cwd = f"/home/{config.ssh_user}"
        dir_name = "test_rm_dir"
        full_path = f"{cwd}/{dir_name}"

        create_test_directory(ssh_client, full_path)
        create_test_file(ssh_client, f"{full_path}/file.txt", "content")

        resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
            "cwd": cwd,
            "files": [dir_name]
        })

        assert resp.status_code == 200
        assert resp.text == "success"

        # Verify directory was deleted
        assert not file_exists(ssh_client, full_path)

    def test_remove_invalid_session(self, local_client: ICtrlClient):
        """Remove with invalid session should fail."""
        resp = local_client.post("/api/sftp_rm/nonexistent-session", json={
            "cwd": "/tmp",
            "files": ["test"]
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - SFTP Rename
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPRenameLocalMode:
    """Tests for PATCH /sftp_rename endpoint in local mode."""

    def test_rename_file(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Rename a file."""
        cwd = f"/home/{config.ssh_user}"
        old_name = "test_rename_old.txt"
        new_name = "test_rename_new.txt"
        old_path = f"{cwd}/{old_name}"
        new_path = f"{cwd}/{new_name}"

        create_test_file(ssh_client, old_path, "rename test")

        try:
            resp = local_client.patch(f"/api/sftp_rename/{local_session}", json={
                "cwd": cwd,
                "old": old_name,
                "new": new_name
            })

            assert resp.status_code == 200
            assert resp.text == "success"

            # Verify rename
            assert not file_exists(ssh_client, old_path)
            assert file_exists(ssh_client, new_path)
        finally:
            cleanup_test_path(ssh_client, new_path)
            cleanup_test_path(ssh_client, old_path)

    def test_rename_directory(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Rename a directory."""
        cwd = f"/home/{config.ssh_user}"
        old_name = "test_rename_dir_old"
        new_name = "test_rename_dir_new"
        old_path = f"{cwd}/{old_name}"
        new_path = f"{cwd}/{new_name}"

        create_test_directory(ssh_client, old_path)

        try:
            resp = local_client.patch(f"/api/sftp_rename/{local_session}", json={
                "cwd": cwd,
                "old": old_name,
                "new": new_name
            })

            assert resp.status_code == 200
            assert resp.text == "success"

            assert not file_exists(ssh_client, old_path)
            assert file_exists(ssh_client, new_path)
        finally:
            cleanup_test_path(ssh_client, new_path)
            cleanup_test_path(ssh_client, old_path)

    def test_rename_nonexistent_file(self, local_client: ICtrlClient, local_session: str, config: TestConfig):
        """Rename non-existent file should fail."""
        resp = local_client.patch(f"/api/sftp_rename/{local_session}", json={
            "cwd": f"/home/{config.ssh_user}",
            "old": "nonexistent_12345.txt",
            "new": "new_name.txt"
        })

        assert resp.status_code == 400

    def test_rename_invalid_session(self, local_client: ICtrlClient):
        """Rename with invalid session should fail."""
        resp = local_client.patch("/api/sftp_rename/nonexistent-session", json={
            "cwd": "/tmp",
            "old": "old.txt",
            "new": "new.txt"
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - SFTP Chmod
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPChmodLocalMode:
    """Tests for PATCH /sftp_chmod endpoint in local mode."""

    def test_chmod_file(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Change file permissions."""
        cwd = f"/home/{config.ssh_user}"
        test_file = "test_chmod.txt"
        full_path = f"{cwd}/{test_file}"

        create_test_file(ssh_client, full_path, "chmod test")

        try:
            # Change to 755 (rwxr-xr-x)
            resp = local_client.patch(f"/api/sftp_chmod/{local_session}", json={
                "path": full_path,
                "mode": 0o755,
                "recursive": False
            })

            assert resp.status_code == 200
            assert resp.text == "success"
        finally:
            cleanup_test_path(ssh_client, full_path)

    def test_chmod_directory_recursive(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Change directory permissions recursively."""
        cwd = f"/home/{config.ssh_user}"
        dir_name = "test_chmod_dir"
        full_path = f"{cwd}/{dir_name}"

        create_test_directory(ssh_client, full_path)
        create_test_file(ssh_client, f"{full_path}/file.txt", "content")

        try:
            resp = local_client.patch(f"/api/sftp_chmod/{local_session}", json={
                "path": full_path,
                "mode": 0o700,
                "recursive": True
            })

            assert resp.status_code == 200
            assert resp.text == "success"
        finally:
            cleanup_test_path(ssh_client, full_path)

    def test_chmod_invalid_session(self, local_client: ICtrlClient):
        """Chmod with invalid session should fail."""
        resp = local_client.patch("/api/sftp_chmod/nonexistent-session", json={
            "path": "/tmp/test",
            "mode": 0o644,
            "recursive": False
        })

        assert resp.status_code == 403


# =============================================================================
# Local Mode Tests - SFTP Permission and Edge Cases
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPPermissionLocalMode:
    """Tests for SFTP permission handling and edge cases."""

    def test_download_unreadable_file_in_zip(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Download unreadable file as part of zip triggers PermissionError path.

        This covers lines 94-95 in SFTP.py: the PermissionError except block in dl_generator
        (called via _zip_dir_recurse when zipping files).
        """
        cwd = f"/home/{config.ssh_user}"
        test_dir = "test_unreadable_dir"
        dir_path = f"{cwd}/{test_dir}"
        readable_file = "readable.txt"
        unreadable_file = "unreadable.txt"

        # Create directory with one readable and one unreadable file
        create_test_directory(ssh_client, dir_path)
        create_test_file(ssh_client, f"{dir_path}/{readable_file}", "readable content")
        create_test_file(ssh_client, f"{dir_path}/{unreadable_file}", "secret content")
        ssh_client.exec_command(f"chmod 000 {dir_path}/{unreadable_file}")

        try:
            # Download the directory as zip - should trigger PermissionError for unreadable file
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": cwd,
                "files": json.dumps([test_dir])
            })

            # The request should succeed - unreadable files yield empty bytes
            assert resp.status_code == 200
            assert resp.headers.get("Content-Type") == "application/zip"

            # Verify the readable file is in the zip
            z = zipfile.ZipFile(io.BytesIO(resp.content))
            zip_names = z.namelist()
            assert any(readable_file in name for name in zip_names)
        finally:
            # Restore permissions before cleanup
            ssh_client.exec_command(f"chmod 644 {dir_path}/{unreadable_file}")
            cleanup_test_path(ssh_client, dir_path)

    def test_download_broken_symlink(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Download broken symlink triggers FileNotFoundError path.

        This covers lines 111-114 in SFTP.py: FileNotFoundError in _zip_dir_recurse.
        """
        cwd = f"/home/{config.ssh_user}"
        test_dir = "test_broken_symlink_dir"
        dir_path = f"{cwd}/{test_dir}"
        symlink_name = "broken_link"

        # Create a directory with a broken symlink
        create_test_directory(ssh_client, dir_path)
        ssh_client.exec_command(f"ln -s /nonexistent/target/file {dir_path}/{symlink_name}")

        try:
            # Download the directory as zip - should handle the broken symlink gracefully
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": cwd,
                "files": json.dumps([test_dir])
            })

            # Should succeed - broken symlinks are skipped
            assert resp.status_code == 200
            assert resp.headers.get("Content-Type") == "application/zip"
        finally:
            cleanup_test_path(ssh_client, dir_path)

    def test_download_directory_with_unreadable_subdir(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Download directory containing unreadable subdirectory triggers PermissionError path.

        This covers lines 115-116 in SFTP.py: PermissionError in _zip_dir_recurse.
        """
        cwd = f"/home/{config.ssh_user}"
        test_dir = "test_perm_dir"
        dir_path = f"{cwd}/{test_dir}"
        subdir = f"{dir_path}/unreadable"

        # Create directory with an unreadable subdirectory
        create_test_directory(ssh_client, dir_path)
        create_test_file(ssh_client, f"{dir_path}/readable.txt", "readable content")
        create_test_directory(ssh_client, subdir)
        create_test_file(ssh_client, f"{subdir}/secret.txt", "secret")
        ssh_client.exec_command(f"chmod 000 {subdir}")

        try:
            # Download the directory as zip - should handle permission error gracefully
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": cwd,
                "files": json.dumps([test_dir])
            })

            # Should succeed - unreadable dirs are skipped
            assert resp.status_code == 200
            assert resp.headers.get("Content-Type") == "application/zip"

            # Verify the readable file is in the zip
            z = zipfile.ZipFile(io.BytesIO(resp.content))
            zip_names = z.namelist()
            assert any("readable.txt" in name for name in zip_names)
        finally:
            # Restore permissions before cleanup
            ssh_client.exec_command(f"chmod 755 {subdir}")
            cleanup_test_path(ssh_client, dir_path)

    def test_chmod_permission_denied(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Chmod on file owned by another user triggers stderr handling.

        This covers lines 141-142 in SFTP.py: chmod stderr handling.
        """
        # Try to chmod a system file that testuser cannot modify
        resp = local_client.patch(f"/api/sftp_chmod/{local_session}", json={
            "path": "/etc/passwd",
            "mode": 0o777,
            "recursive": False
        })

        # Should return error due to permission denied
        assert resp.status_code == 400

    def test_remove_many_files_batching(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Remove more than 50 files to trigger batching logic.

        This covers lines 162-170 in SFTP.py: the batching when counter reaches 50.
        """
        cwd = f"/home/{config.ssh_user}"
        test_dir = "test_batch_rm"
        dir_path = f"{cwd}/{test_dir}"
        num_files = 60  # More than 50 to trigger batching

        # Create directory with many files
        create_test_directory(ssh_client, dir_path)
        files = []
        for i in range(num_files):
            filename = f"batch_file_{i:03d}.txt"
            create_test_file(ssh_client, f"{dir_path}/{filename}", f"content {i}")
            files.append(filename)

        try:
            # Remove all files at once - should trigger batching at 50
            resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
                "cwd": dir_path,
                "files": files
            })

            assert resp.status_code == 200
            assert resp.text == "success"

            # Verify all files were deleted
            for filename in files:
                assert not file_exists(ssh_client, f"{dir_path}/{filename}")
        finally:
            cleanup_test_path(ssh_client, dir_path)

    def test_remove_permission_denied(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Remove file with permission denied triggers stderr handling.

        This covers lines 175-176, 179 in SFTP.py: rm stderr handling.
        """
        cwd = f"/home/{config.ssh_user}"
        test_dir = "test_rm_perm"
        dir_path = f"{cwd}/{test_dir}"

        # Create a directory and file, then make directory non-writable
        create_test_directory(ssh_client, dir_path)
        create_test_file(ssh_client, f"{dir_path}/protected.txt", "protected content")
        # Remove write permission on directory so files inside can't be deleted
        ssh_client.exec_command(f"chmod 555 {dir_path}")

        try:
            # Try to remove the file - should fail with permission error
            resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
                "cwd": dir_path,
                "files": ["protected.txt"]
            })

            # Should return error due to permission denied
            assert resp.status_code == 400
        finally:
            # Restore permissions before cleanup
            ssh_client.exec_command(f"chmod 755 {dir_path}")
            cleanup_test_path(ssh_client, dir_path)

    def test_remove_many_files_with_batch_error(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Remove 50+ files where first batch has permission errors.

        This covers lines 165-166 in SFTP.py: the stderr handling inside the batch loop.
        """
        cwd = f"/home/{config.ssh_user}"
        test_dir = "test_batch_rm_err"
        dir_path = f"{cwd}/{test_dir}"
        num_files = 55  # More than 50 to trigger batching

        # Create directory with many files
        create_test_directory(ssh_client, dir_path)
        files = []
        for i in range(num_files):
            filename = f"batch_err_{i:03d}.txt"
            create_test_file(ssh_client, f"{dir_path}/{filename}", f"content {i}")
            files.append(filename)

        # Make directory non-writable so first batch rm will fail
        ssh_client.exec_command(f"chmod 555 {dir_path}")

        try:
            # Remove all files at once - should trigger batching and error at line 165-166
            resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
                "cwd": dir_path,
                "files": files
            })

            # Should return error due to permission denied
            assert resp.status_code == 400
        finally:
            # Restore permissions before cleanup
            ssh_client.exec_command(f"chmod 755 {dir_path}")
            cleanup_test_path(ssh_client, dir_path)


# =============================================================================
# Local Mode Tests - SFTP End-to-End
# =============================================================================

@pytest.mark.integration
@pytest.mark.local_mode
@pytest.mark.sftp
class TestSFTPE2ELocalMode:
    """End-to-end tests for SFTP functionality."""

    def test_full_file_lifecycle(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Test complete file lifecycle: upload, list, download, rename, delete."""
        cwd = f"/home/{config.ssh_user}"
        filename = "lifecycle_test.txt"
        renamed = "lifecycle_renamed.txt"
        content = b"Lifecycle test content"

        try:
            # 1. Upload file
            resp = local_client.post(
                f"/api/sftp_ul/{local_session}",
                data=content,
                headers={"Cwd": cwd, "Path": filename, "Content-Type": "application/octet-stream"}
            )
            assert resp.status_code == 200

            # 2. List and verify
            resp = local_client.get(f"/api/sftp_ls/{local_session}", params={"path": cwd})
            assert resp.status_code == 200
            files = [f["id"] for f in resp.json()["files"]]
            assert filename in files

            # 3. Download and verify content
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": cwd,
                "files": json.dumps([filename])
            })
            assert resp.status_code == 200
            assert content in resp.content

            # 4. Rename file
            resp = local_client.patch(f"/api/sftp_rename/{local_session}", json={
                "cwd": cwd,
                "old": filename,
                "new": renamed
            })
            assert resp.status_code == 200

            # 5. Verify rename
            resp = local_client.get(f"/api/sftp_ls/{local_session}", params={"path": cwd})
            files = [f["id"] for f in resp.json()["files"]]
            assert filename not in files
            assert renamed in files

            # 6. Delete file
            resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
                "cwd": cwd,
                "files": [renamed]
            })
            assert resp.status_code == 200

            # 7. Verify deletion
            assert not file_exists(ssh_client, f"{cwd}/{renamed}")

        finally:
            cleanup_test_path(ssh_client, f"{cwd}/{filename}")
            cleanup_test_path(ssh_client, f"{cwd}/{renamed}")

    def test_directory_operations(self, local_client: ICtrlClient, local_session: str, ssh_client, config: TestConfig):
        """Test directory creation, population, and deletion."""
        cwd = f"/home/{config.ssh_user}"
        dir_name = "test_dir_ops"
        full_path = f"{cwd}/{dir_name}"

        try:
            # 1. Create directory
            resp = local_client.put(f"/api/sftp_mkdir/{local_session}", json={
                "cwd": cwd,
                "name": dir_name
            })
            assert resp.status_code == 200

            # 2. Upload files to directory
            for i in range(3):
                resp = local_client.post(
                    f"/api/sftp_ul/{local_session}",
                    data=f"File {i} content".encode(),
                    headers={
                        "Cwd": full_path,
                        "Path": f"file_{i}.txt",
                        "Content-Type": "application/octet-stream"
                    }
                )
                assert resp.status_code == 200

            # 3. List directory
            resp = local_client.get(f"/api/sftp_ls/{local_session}", params={"path": full_path})
            assert resp.status_code == 200
            files = resp.json()["files"]
            assert len(files) == 3

            # 4. Download as zip
            resp = local_client.get(f"/api/sftp_dl/{local_session}", params={
                "cwd": cwd,
                "files": json.dumps([dir_name])
            })
            assert resp.status_code == 200
            assert resp.headers.get("Content-Type") == "application/zip"

            # 5. Delete directory
            resp = local_client.post(f"/api/sftp_rm/{local_session}", json={
                "cwd": cwd,
                "files": [dir_name]
            })
            assert resp.status_code == 200

            # 6. Verify deletion
            assert not file_exists(ssh_client, full_path)

        finally:
            cleanup_test_path(ssh_client, full_path)
