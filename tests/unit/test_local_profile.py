"""
Unit tests for LocalProfile class.

Note: Since tests/conftest.py loads the application module before unit tests run,
we access the module via sys.modules to avoid import conflicts.
"""

import base64
import json
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open


def get_local_profile_module():
    """Get the LocalProfile module from sys.modules (already loaded by conftest)."""
    # Ensure the application is imported (done by conftest.py)
    if 'application' not in sys.modules:
        # Set up sys.argv for standalone execution
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.Profile.LocalProfile']


class TestLocalProfileInit:
    """Tests for LocalProfile initialization."""

    def test_init_creates_empty_profile_when_file_not_found(self, tmp_path):
        """When profile file doesn't exist, creates empty profile."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(tmp_path / 'nonexistent.json')):
            profile = LocalProfile()
            assert profile._profile == {"version": _PROFILE_VERSION, "sessions": {}}

    def test_init_loads_existing_profile(self, tmp_path):
        """When profile file exists with valid data, loads it."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {
                    "host": "example.com",
                    "username": "testuser"
                }
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            assert profile._profile["sessions"]["test-session-id"]["host"] == "example.com"
            assert profile._profile["sessions"]["test-session-id"]["username"] == "testuser"

    def test_init_rejects_wrong_version(self, tmp_path):
        """When profile file has wrong version, uses empty profile."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": 999,  # Wrong version
            "sessions": {
                "test-session-id": {"host": "example.com"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            # Should have empty sessions due to version mismatch
            assert profile._profile == {"version": _PROFILE_VERSION, "sessions": {}}

    def test_init_handles_missing_version(self, tmp_path):
        """When profile file has no version field, uses empty profile."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {"sessions": {}}  # No version
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            assert profile._profile == {"version": _PROFILE_VERSION, "sessions": {}}

    def test_init_handles_invalid_json(self, tmp_path):
        """When profile file has invalid JSON, uses empty profile."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        profile_path.write_text("not valid json {{{")

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            assert profile._profile == {"version": _PROFILE_VERSION, "sessions": {}}


class TestLocalProfileNotImplementedMethods:
    """Tests for methods that raise NotImplementedError in local mode."""

    def test_login_raises_not_implemented(self, tmp_path):
        """login() should raise NotImplementedError in local mode."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(tmp_path / 'profile.json')):
            profile = LocalProfile()
            with pytest.raises(NotImplementedError):
                profile.login("user", "pass")

    def test_logout_raises_not_implemented(self, tmp_path):
        """logout() should raise NotImplementedError in local mode."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(tmp_path / 'profile.json')):
            profile = LocalProfile()
            with pytest.raises(NotImplementedError):
                profile.logout()

    def test_add_user_raises_not_implemented(self, tmp_path):
        """add_user() should raise NotImplementedError in local mode."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(tmp_path / 'profile.json')):
            profile = LocalProfile()
            with pytest.raises(NotImplementedError):
                profile.add_user("user", "pass", "email@test.com")

    def test_activate_user_raises_not_implemented(self, tmp_path):
        """activate_user() should raise NotImplementedError in local mode."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(tmp_path / 'profile.json')):
            profile = LocalProfile()
            with pytest.raises(NotImplementedError):
                # activate_user takes userid and code
                profile.activate_user("userid", "activation_code")

    def test_send_activation_email_raises_not_implemented(self, tmp_path):
        """send_activation_email() should raise NotImplementedError in local mode."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(tmp_path / 'profile.json')):
            profile = LocalProfile()
            with pytest.raises(NotImplementedError):
                profile.send_activation_email("email@test.com")


class TestLocalProfileQuery:
    """Tests for the query method."""

    def test_query_returns_profile(self, tmp_path):
        """query() should return the profile data."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "session1": {"host": "host1.com", "username": "user1"},
                "session2": {"host": "host2.com", "username": "user2"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            result = profile.query()
            assert result == test_profile


class TestLocalProfileAddSession:
    """Tests for add_session method."""

    def test_add_session_without_conn(self, tmp_path):
        """add_session() without connection stores session data."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            # Mock save_profile to verify it's called
            with patch.object(profile, 'save_profile') as mock_save:
                result = profile.add_session("test-host.com", "testuser", None)

                # Check return value is (True, '')
                assert result == (True, '')

                # Verify session was added
                sessions = profile._profile["sessions"]
                assert len(sessions) == 1
                session_id = list(sessions.keys())[0]
                assert sessions[session_id]["host"] == "test-host.com"
                assert sessions[session_id]["username"] == "testuser"
                mock_save.assert_called_once()

    def test_add_session_with_conn_success(self, tmp_path):
        """add_session() with connection saves SSH keys."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'
        key_path = tmp_path / 'keys'
        key_path.mkdir()

        # Create a mock SSH connection with save_keys method
        mock_conn = MagicMock()
        mock_conn.save_keys.return_value = (True, '')

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)), \
             patch.object(local_profile_module, 'PRIVATE_KEY_PATH', str(key_path)):

            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                result = profile.add_session("test-host.com", "testuser", mock_conn)

                assert result == (True, '')
                mock_conn.save_keys.assert_called_once()
                mock_save.assert_called_once()

    def test_add_session_with_conn_save_keys_failure(self, tmp_path):
        """add_session() returns error if save_keys fails."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'
        key_path = tmp_path / 'keys'
        key_path.mkdir()

        # Create a mock SSH connection that fails to save keys
        mock_conn = MagicMock()
        mock_conn.save_keys.return_value = (False, 'Key save failed')

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)), \
             patch.object(local_profile_module, 'PRIVATE_KEY_PATH', str(key_path)):

            profile = LocalProfile()

            result = profile.add_session("test-host.com", "testuser", mock_conn)

            # Should return failure
            assert result == (False, 'Key save failed')


class TestLocalProfileDeleteSession:
    """Tests for delete_session method."""

    def test_delete_session_success(self, tmp_path):
        """delete_session() removes session and key file."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        key_path = tmp_path / 'keys'
        key_path.mkdir()

        # Create key file
        key_file = key_path / 'test-session-id'
        key_file.write_text("key content")

        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)), \
             patch.object(local_profile_module, 'PRIVATE_KEY_PATH', str(key_path)):

            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                result = profile.delete_session("test-session-id")

                assert result == (True, '')
                assert "test-session-id" not in profile._profile["sessions"]
                assert not key_file.exists()
                mock_save.assert_called_once()

    def test_delete_session_nonexistent(self, tmp_path):
        """delete_session() with nonexistent session returns failure."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            result = profile.delete_session("nonexistent-id")
            assert result[0] is False
            assert "does not exist" in result[1]

    def test_delete_session_no_key_file(self, tmp_path):
        """delete_session() works even if key file doesn't exist."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        key_path = tmp_path / 'keys'
        key_path.mkdir()

        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)), \
             patch.object(local_profile_module, 'PRIVATE_KEY_PATH', str(key_path)):

            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                # Should not raise even without key file
                result = profile.delete_session("test-session-id")

                assert result == (True, '')
                assert "test-session-id" not in profile._profile["sessions"]
                mock_save.assert_called_once()


class TestLocalProfileChangeHost:
    """Tests for change_host method."""

    def test_change_host_success(self, tmp_path):
        """change_host() updates host for existing session."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "old-host.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                result = profile.change_host("test-session-id", "new-host.com")

                assert result == (True, '')
                assert profile._profile["sessions"]["test-session-id"]["host"] == "new-host.com"
                mock_save.assert_called_once()

    def test_change_host_nonexistent_session(self, tmp_path):
        """change_host() with nonexistent session returns failure."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            result = profile.change_host("nonexistent-id", "new-host.com")
            assert result[0] is False
            assert "does not exist" in result[1]


class TestLocalProfileSaveProfile:
    """Tests for save_profile method."""

    def test_save_profile_writes_json(self, tmp_path):
        """save_profile() writes profile to JSON file."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            profile._profile["sessions"]["new-session"] = {"host": "test.com", "username": "user"}
            profile.save_profile()

            # Read back and verify
            with open(profile_path) as f:
                saved_data = json.load(f)
            assert "new-session" in saved_data["sessions"]
            assert saved_data["sessions"]["new-session"]["host"] == "test.com"


class TestLocalProfileGetSessionInfo:
    """Tests for get_session_info method."""

    def test_get_session_info_success(self, tmp_path):
        """get_session_info() returns session info tuple."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        key_path = tmp_path / 'keys'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {
                    "host": "example.com",
                    "username": "testuser",
                    "nickname": "MyServer"
                }
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)), \
             patch.object(local_profile_module, 'PRIVATE_KEY_PATH', str(key_path)):
            profile = LocalProfile()
            # Returns (host, username, key_path, None, nickname)
            host, username, key_path_result, _, nickname = profile.get_session_info("test-session-id")

            assert host == "example.com"
            assert username == "testuser"
            assert nickname == "MyServer"
            assert str(key_path) in key_path_result

    def test_get_session_info_no_nickname(self, tmp_path):
        """get_session_info() returns None for missing nickname."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        key_path = tmp_path / 'keys'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {
                    "host": "example.com",
                    "username": "testuser"
                }
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)), \
             patch.object(local_profile_module, 'PRIVATE_KEY_PATH', str(key_path)):
            profile = LocalProfile()
            host, username, _, _, nickname = profile.get_session_info("test-session-id")

            assert host == "example.com"
            assert username == "testuser"
            assert nickname is None

    def test_get_session_info_nonexistent(self, tmp_path):
        """get_session_info() returns Nones for nonexistent session."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            # Returns all Nones for nonexistent session
            result = profile.get_session_info("nonexistent-id")
            assert result == (None, None, None, None, None)


class TestLocalProfileSetSessionNickname:
    """Tests for set_session_nickname method."""

    def test_set_nickname_success(self, tmp_path):
        """set_session_nickname() updates nickname."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                # Nickname max length is 8
                result = profile.set_session_nickname("test-session-id", "MyServer")

                assert result == (True, '')
                assert profile._profile["sessions"]["test-session-id"]["nickname"] == "MyServer"
                mock_save.assert_called_once()

    def test_set_nickname_too_long(self, tmp_path):
        """set_session_nickname() rejects nicknames over 8 chars."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            result = profile.set_session_nickname("test-session-id", "TooLongNickname")

            assert result[0] is False
            assert "too long" in result[1]

    def test_set_nickname_empty_deletes(self, tmp_path):
        """set_session_nickname() with empty string removes nickname."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {
                    "host": "example.com",
                    "username": "testuser",
                    "nickname": "OldNick"
                }
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                result = profile.set_session_nickname("test-session-id", "")

                assert result == (True, '')
                assert "nickname" not in profile._profile["sessions"]["test-session-id"]
                mock_save.assert_called_once()

    def test_set_nickname_empty_no_existing(self, tmp_path):
        """set_session_nickname() with empty string when no nickname exists."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                # Should not raise, just does nothing
                result = profile.set_session_nickname("test-session-id", "")

                assert result == (True, '')
                assert "nickname" not in profile._profile["sessions"]["test-session-id"]
                mock_save.assert_called_once()

    def test_set_nickname_nonexistent_session(self, tmp_path):
        """set_session_nickname() returns failure for nonexistent session."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            result = profile.set_session_nickname("nonexistent-id", "Nickname")
            assert result[0] is False
            assert "does not exist" in result[1]


class TestLocalProfileVncCredentials:
    """Tests for VNC credentials methods."""

    def test_set_vnc_credentials_success(self, tmp_path):
        """set_session_vnc_credentials() stores base64 encoded JSON credentials."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                # credentials is a dict that gets JSON-encoded then base64-encoded
                credentials = {"password": "vnc_password", "display": 1}
                result = profile.set_session_vnc_credentials("test-session-id", credentials)

                assert result == (True, '')
                encoded = profile._profile["sessions"]["test-session-id"]["vnc_credentials"]
                decoded = json.loads(base64.b64decode(encoded).decode())
                assert decoded == credentials
                mock_save.assert_called_once()

    def test_set_vnc_credentials_none_deletes(self, tmp_path):
        """set_session_vnc_credentials() with None removes credentials."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        old_creds = {"password": "old_pass"}
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {
                    "host": "example.com",
                    "username": "testuser",
                    "vnc_credentials": base64.b64encode(json.dumps(old_creds).encode()).decode()
                }
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                result = profile.set_session_vnc_credentials("test-session-id", None)

                assert result == (True, '')
                assert "vnc_credentials" not in profile._profile["sessions"]["test-session-id"]
                mock_save.assert_called_once()

    def test_set_vnc_credentials_none_no_existing(self, tmp_path):
        """set_session_vnc_credentials() with None when no credentials exist."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            with patch.object(profile, 'save_profile') as mock_save:
                # Should not raise
                result = profile.set_session_vnc_credentials("test-session-id", None)

                assert result == (True, '')
                assert "vnc_credentials" not in profile._profile["sessions"]["test-session-id"]
                mock_save.assert_called_once()

    def test_set_vnc_credentials_nonexistent_session(self, tmp_path):
        """set_session_vnc_credentials() returns failure for nonexistent session."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            result = profile.set_session_vnc_credentials("nonexistent-id", {"password": "test"})
            assert result[0] is False
            assert "does not exist" in result[1]

    def test_get_vnc_credentials_success(self, tmp_path):
        """get_session_vnc_credentials() returns decoded credentials."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        credentials = {"password": "my_vnc_pass", "display": 2}
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {
                    "host": "example.com",
                    "username": "testuser",
                    "vnc_credentials": base64.b64encode(json.dumps(credentials).encode()).decode()
                }
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            success, result = profile.get_session_vnc_credentials("test-session-id")
            assert success is True
            assert result == credentials

    def test_get_vnc_credentials_not_set(self, tmp_path):
        """get_session_vnc_credentials() returns empty string when not set."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            success, result = profile.get_session_vnc_credentials("test-session-id")
            assert success is True
            assert result == ''

    def test_get_vnc_credentials_nonexistent_session(self, tmp_path):
        """get_session_vnc_credentials() returns failure for nonexistent session."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            success, message = profile.get_session_vnc_credentials("nonexistent-id")
            assert success is False
            assert "does not exist" in message


class TestLocalProfileGetUser:
    """Tests for get_user method."""

    def test_get_user_returns_dummy_user(self, tmp_path):
        """get_user() returns a DummyUser object with id=0 in local mode."""
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            result = profile.get_user()

            # Should return a DummyUser object with id=0
            assert hasattr(result, 'id')
            assert result.id == 0


class TestLocalProfileTamperedFile:
    """Tests for tampered/deleted/permission-changed profile scenarios."""

    @pytest.mark.unit
    def test_init_with_permission_denied_file(self, tmp_path):
        """When profile file has no read permission, uses empty profile.

        This covers lines 69-73 in LocalProfile.py.
        """
        import os
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {"test-session": {"host": "test.com", "username": "user"}}
        }
        profile_path.write_text(json.dumps(test_profile))

        # Remove read permission
        os.chmod(profile_path, 0o000)

        try:
            with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
                profile = LocalProfile()
                # Should fall back to empty profile
                assert profile._profile == {"version": _PROFILE_VERSION, "sessions": {}}
        finally:
            # Restore permissions for cleanup
            os.chmod(profile_path, 0o644)

    @pytest.mark.unit
    def test_save_profile_permission_denied(self, tmp_path):
        """When save_profile cannot write, raises exception.

        This covers lines 125-127 in LocalProfile.py.
        """
        import os
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'
        # Create an empty file first
        profile_path.write_text('{}')

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            # Make the file unwritable
            os.chmod(profile_path, 0o444)

            try:
                with pytest.raises(PermissionError):
                    profile.save_profile()
            finally:
                # Restore permissions for cleanup
                os.chmod(profile_path, 0o644)

    @pytest.mark.unit
    def test_save_profile_directory_not_writable(self, tmp_path):
        """When profile directory is not writable, raises exception.

        This covers lines 125-127 in LocalProfile.py.
        """
        import os
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        # Create a subdirectory for the profile
        profile_dir = tmp_path / 'config'
        profile_dir.mkdir()
        profile_path = profile_dir / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            # Make the directory read-only
            os.chmod(profile_dir, 0o555)

            try:
                with pytest.raises(PermissionError):
                    profile.save_profile()
            finally:
                # Restore permissions for cleanup
                os.chmod(profile_dir, 0o755)

    @pytest.mark.unit
    def test_init_profile_deleted_between_load_and_access(self, tmp_path):
        """Profile file is deleted after LocalProfile was initialized.

        Simulates a tampered/deleted profile scenario. Operations after init
        should still work with in-memory profile.
        """
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {"test-session": {"host": "test.com", "username": "user"}}
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            # Profile loaded successfully
            assert "test-session" in profile._profile["sessions"]

            # Now delete the file (simulating external tampering)
            profile_path.unlink()

            # In-memory profile should still work for queries
            assert profile.query()["sessions"]["test-session"]["host"] == "test.com"

            # But save_profile will create a new file
            profile.save_profile()
            assert profile_path.exists()

    @pytest.mark.unit
    def test_init_profile_corrupted_mid_session(self, tmp_path):
        """Profile file is corrupted with invalid JSON.

        This covers lines 69-73 in LocalProfile.py.
        """
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        # Write corrupted JSON (truncated/binary garbage)
        profile_path.write_bytes(b'{"version": 1, "sessions": {"test": {"host":\x00\x01\xff')

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()
            # Should fall back to empty profile due to JSON decode error
            assert profile._profile == {"version": _PROFILE_VERSION, "sessions": {}}

    @pytest.mark.unit
    def test_delete_session_handles_key_file_already_deleted(self, tmp_path):
        """delete_session handles case where key file was already deleted.

        This covers lines 103-104 in LocalProfile.py.
        """
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile
        _PROFILE_VERSION = local_profile_module._PROFILE_VERSION

        profile_path = tmp_path / 'profile.json'
        key_path = tmp_path / 'keys'
        key_path.mkdir()

        test_profile = {
            "version": _PROFILE_VERSION,
            "sessions": {
                "test-session-id": {"host": "example.com", "username": "testuser"}
            }
        }
        profile_path.write_text(json.dumps(test_profile))

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)), \
             patch.object(local_profile_module, 'PRIVATE_KEY_PATH', str(key_path)):

            profile = LocalProfile()

            # Don't create the key file - simulating it was already deleted
            # The delete_session should handle FileNotFoundError gracefully
            result = profile.delete_session("test-session-id")

            assert result == (True, '')
            assert "test-session-id" not in profile._profile["sessions"]

    @pytest.mark.unit
    def test_change_host_nonexistent_session(self, tmp_path):
        """change_host returns error for nonexistent session.

        This covers line 113 in LocalProfile.py.
        """
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            result = profile.change_host("nonexistent-session-id", "new-host.com")

            assert result[0] is False
            assert "does not exist" in result[1]

    @pytest.mark.unit
    def test_get_vnc_credentials_nonexistent_session(self, tmp_path):
        """get_session_vnc_credentials returns error for nonexistent session.

        This covers line 182 in LocalProfile.py.
        """
        local_profile_module = get_local_profile_module()
        LocalProfile = local_profile_module.LocalProfile

        profile_path = tmp_path / 'profile.json'

        with patch.object(local_profile_module, 'USER_PROFILE_PATH', str(profile_path)):
            profile = LocalProfile()

            success, message = profile.get_session_vnc_credentials("nonexistent-session-id")

            assert success is False
            assert "does not exist" in message
