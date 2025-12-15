"""
Unit tests for Profile/DBProfile.py.

Tests the database profile implementation with mocked database.
These tests use mocking to execute DBProfile code without a real database.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock, PropertyMock, mock_open
import uuid
import base64
import json

# Set up environment variables BEFORE any imports that might need them
os.environ['ICTRL_DBPASSWD'] = 'testpasswd'
os.environ['ICTRL_DBADDR'] = 'localhost:5432'
os.environ['ICTRL_RESEND_COOLDOWN_SEC'] = '2'


def get_dbprofile_module():
    """Get the DBProfile module."""
    # The module gets imported via conftest's application import
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application

    # Import directly if not in sys.modules yet
    if 'application.Profile.DBProfile' not in sys.modules:
        from application.Profile import DBProfile
        return DBProfile
    return sys.modules['application.Profile.DBProfile']


class TestActivationType:
    """Tests for ActivationType enum."""

    @pytest.mark.unit
    def test_activation_type_values(self):
        """Test ActivationType enum values."""
        dbp_module = get_dbprofile_module()

        assert dbp_module.ActivationType.NOT_ACTIVATED == 0
        assert dbp_module.ActivationType.NORMAL_USER == 1


class TestDBProfileConstants:
    """Tests for DBProfile module constants."""

    @pytest.mark.unit
    def test_activation_ttl_second(self):
        """Test ACTIVATION_TTL_SECOND is 30 minutes."""
        dbp_module = get_dbprofile_module()

        assert dbp_module.ACTIVATION_TTL_SECOND == 60 * 30

    @pytest.mark.unit
    def test_resend_cooldown_configurable(self):
        """Test RESEND_COOLDOWN_TTL_SECOND is configurable via env."""
        dbp_module = get_dbprofile_module()

        # Value can be 2 (from env) or 30 (default)
        assert dbp_module.RESEND_COOLDOWN_TTL_SECOND >= 2

    @pytest.mark.unit
    def test_session_crypt_salt_is_bytes(self):
        """Test SESSION_CRYPT_SALT is bytes."""
        dbp_module = get_dbprofile_module()

        assert isinstance(dbp_module.SESSION_CRYPT_SALT, bytes)


class TestDBProfileInit:
    """Tests for DBProfile.__init__ method."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock Flask app."""
        app = MagicMock()
        app.config = {}
        return app

    @pytest.mark.unit
    def test_init_sets_database_uri(self, mock_app):
        """Test __init__ sets SQLALCHEMY_DATABASE_URI."""
        from application.Profile import DBProfile as dbp_module

        with patch.object(dbp_module, 'SQLAlchemy') as mock_sqlalchemy, \
             patch('builtins.open', mock_open(read_data='<html>{username}{userid}{code}{expire_min}</html>')):
            mock_db = MagicMock()
            mock_db.Model = MagicMock()
            mock_db.engine = MagicMock()
            mock_sqlalchemy.return_value = mock_db

            profile = dbp_module.DBProfile(mock_app)

            expected_uri = "postgresql://postgres:testpasswd@localhost:5432"
            assert mock_app.config["SQLALCHEMY_DATABASE_URI"] == expected_uri

    @pytest.mark.unit
    def test_init_creates_activation_cache(self, mock_app):
        """Test __init__ creates activation cache."""
        from application.Profile import DBProfile as dbp_module

        with patch.object(dbp_module, 'SQLAlchemy') as mock_sqlalchemy, \
             patch('builtins.open', mock_open(read_data='<html></html>')):
            mock_db = MagicMock()
            mock_db.Model = MagicMock()
            mock_db.engine = MagicMock()
            mock_sqlalchemy.return_value = mock_db

            profile = dbp_module.DBProfile(mock_app)

            assert profile.activation_cache is not None
            assert profile.resend_cooldown is not None


class TestDBProfileLogout:
    """Tests for DBProfile.logout method."""

    @pytest.mark.unit
    def test_logout_pops_userid(self):
        """Test logout removes userid from session."""
        dbp_module = get_dbprofile_module()

        mock_session = {'userid': 123}
        with patch.object(dbp_module, 'flask_session', mock_session):
            result = dbp_module.DBProfile.logout()

            assert result is True
            assert 'userid' not in mock_session


class TestDBProfileLogin:
    """Tests for DBProfile.login method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.salt = b'$2b$12$test_salt_value_here'
        profile.activation_cache = {}
        profile.resend_cooldown = {}
        profile.User = MagicMock()
        return profile

    @pytest.mark.unit
    def test_login_wrong_username_aborts(self, mock_profile):
        """Test login aborts with ACCOUNT_WRONG_USERNAME."""
        dbp_module = get_dbprofile_module()

        mock_profile.User.query.filter_by.return_value.first.return_value = None

        with patch.object(dbp_module, 'abort') as mock_abort:
            mock_abort.side_effect = Exception('abort called')
            try:
                mock_profile.login('nonexistent', 'password')
            except Exception:
                pass

            mock_abort.assert_called_once_with(403, 'ACCOUNT_WRONG_USERNAME')

    @pytest.mark.unit
    def test_login_not_activated_aborts(self, mock_profile):
        """Test login aborts with ACCOUNT_NOT_ACTIVATED."""
        dbp_module = get_dbprofile_module()

        mock_user = MagicMock()
        mock_user.activation_type = dbp_module.ActivationType.NOT_ACTIVATED
        mock_profile.User.query.filter_by.return_value.first.return_value = mock_user

        with patch.object(dbp_module, 'abort') as mock_abort:
            mock_abort.side_effect = Exception('abort called')
            try:
                mock_profile.login('testuser', 'password')
            except Exception:
                pass

            mock_abort.assert_called_once_with(401, 'ACCOUNT_NOT_ACTIVATED')

    @pytest.mark.unit
    def test_login_wrong_password_aborts(self, mock_profile):
        """Test login aborts with ACCOUNT_WRONG_PASSWORD."""
        dbp_module = get_dbprofile_module()

        mock_user = MagicMock()
        mock_user.activation_type = dbp_module.ActivationType.NORMAL_USER
        mock_user.password = '$2b$12$wronghash'
        mock_profile.User.query.filter_by.return_value.first.return_value = mock_user

        with patch.object(dbp_module, 'abort') as mock_abort, \
             patch.object(dbp_module, 'bcrypt') as mock_bcrypt:
            mock_bcrypt.checkpw.return_value = False
            mock_abort.side_effect = Exception('abort called')

            try:
                mock_profile.login('testuser', 'wrongpassword')
            except Exception:
                pass

            mock_abort.assert_called_once_with(403, 'ACCOUNT_WRONG_PASSWORD')

    @pytest.mark.unit
    def test_login_success_sets_session(self, mock_profile):
        """Test successful login sets flask session."""
        dbp_module = get_dbprofile_module()

        mock_user = MagicMock()
        mock_user.id = 42
        mock_user.activation_type = dbp_module.ActivationType.NORMAL_USER
        mock_user.password = '$2b$12$validhash'
        mock_profile.User.query.filter_by.return_value.first.return_value = mock_user

        mock_session = {}
        with patch.object(dbp_module, 'flask_session', mock_session), \
             patch.object(dbp_module, 'bcrypt') as mock_bcrypt:
            mock_bcrypt.checkpw.return_value = True

            result = mock_profile.login('testuser', 'correctpassword')

            assert result is True
            assert mock_session['userid'] == 42
            assert 'session_crypt_key' in mock_session


class TestDBProfileAddUser:
    """Tests for DBProfile.add_user method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()
        import bcrypt

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.salt = bcrypt.gensalt()  # Use real salt
        profile.activation_cache = {}
        profile.resend_cooldown = {}
        profile.User = MagicMock()
        return profile

    @pytest.mark.unit
    def test_add_user_weak_password_aborts(self, mock_profile):
        """Test add_user aborts with weak password."""
        dbp_module = get_dbprofile_module()

        with patch.object(dbp_module, 'abort') as mock_abort, \
             patch.object(dbp_module, 'validate_password') as mock_validate:
            mock_validate.return_value = (False, 'Password too short')
            mock_abort.side_effect = Exception('abort called')

            try:
                mock_profile.add_user('testuser', 'weak', 'test@mail.utoronto.ca')
            except Exception:
                pass

            mock_abort.assert_called_once_with(422, 'Password too short')

    @pytest.mark.unit
    def test_add_user_duplicate_username_aborts(self, mock_profile):
        """Test add_user aborts with ACCOUNT_DUPLICATE_USERNAME."""
        dbp_module = get_dbprofile_module()
        import sqlalchemy

        # Need to mock save_profile and send_activation_email too
        mock_profile.save_profile = MagicMock()
        mock_profile.send_activation_email = MagicMock()

        with patch.object(dbp_module, 'abort') as mock_abort, \
             patch.object(dbp_module, 'validate_password') as mock_validate:
            mock_validate.return_value = (True, None)

            # Simulate IntegrityError with username constraint
            error = sqlalchemy.exc.IntegrityError('test', 'test', Exception('user_username_key'))
            error.orig = MagicMock()
            error.orig.args = ['user_username_key violation']
            mock_profile.save_profile.side_effect = error
            mock_abort.side_effect = Exception('abort called')

            try:
                mock_profile.add_user('testuser', 'ValidPass1!', 'test@mail.utoronto.ca')
            except Exception:
                pass

            mock_abort.assert_called_with(422, 'ACCOUNT_DUPLICATE_USERNAME')


class TestDBProfileQuery:
    """Tests for DBProfile.query method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.User = MagicMock()
        profile.Session = MagicMock()
        return profile

    @pytest.mark.unit
    def test_query_returns_profile_dict(self, mock_profile):
        """Test query returns profile dictionary with sessions."""
        mock_session1 = MagicMock()
        mock_session1.id = uuid.uuid4()
        mock_session1.host = 'host1.example.com'
        mock_session1.nickname = 'Host1'
        mock_session1.username = 'user1'

        mock_user = MagicMock()
        mock_user.sessions = [mock_session1]

        with patch.object(mock_profile, 'get_user', return_value=mock_user):
            result = mock_profile.query()

            assert 'sessions' in result
            assert mock_session1.id.hex in result['sessions']
            assert result['sessions'][mock_session1.id.hex]['host'] == 'host1.example.com'


class TestDBProfileActivateUser:
    """Tests for DBProfile.activate_user method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.activation_cache = {}
        profile.User = MagicMock()
        return profile

    @pytest.mark.unit
    def test_activate_user_no_cached_code(self, mock_profile):
        """Test activate_user returns False when no cached code."""
        result = mock_profile.activate_user('123', 'wrong-code')
        assert result is False

    @pytest.mark.unit
    def test_activate_user_wrong_code(self, mock_profile):
        """Test activate_user returns False with wrong code."""
        mock_profile.activation_cache['123'] = 'correct-code'

        result = mock_profile.activate_user('123', 'wrong-code')
        assert result is False

    @pytest.mark.unit
    def test_activate_user_success(self, mock_profile):
        """Test activate_user returns True with correct code."""
        dbp_module = get_dbprofile_module()

        mock_profile.activation_cache['123'] = 'correct-code'
        mock_profile.save_profile = MagicMock()

        mock_user = MagicMock()
        mock_profile.User.query.filter_by.return_value.first.return_value = mock_user

        result = mock_profile.activate_user('123', 'correct-code')

        assert result is True
        assert mock_user.activation_type == dbp_module.ActivationType.NORMAL_USER


class TestDBProfileDeleteSession:
    """Tests for DBProfile.delete_session method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.Session = MagicMock()
        return profile

    @pytest.mark.unit
    def test_delete_session_not_found(self, mock_profile):
        """Test delete_session returns False when session not found."""
        mock_profile._get_session = MagicMock(return_value=None)

        status, reason = mock_profile.delete_session('test-id')

        assert status is False
        assert 'does not exist' in reason

    @pytest.mark.unit
    def test_delete_session_success(self, mock_profile):
        """Test delete_session returns True on success."""
        mock_session = MagicMock()
        mock_profile._get_session = MagicMock(return_value=mock_session)
        mock_profile.save_profile = MagicMock()

        status, reason = mock_profile.delete_session('test-id')

        assert status is True
        assert reason == ''
        mock_profile.db.session.delete.assert_called_once_with(mock_session)


class TestDBProfileChangeHost:
    """Tests for DBProfile.change_host method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.Session = MagicMock()
        return profile

    @pytest.mark.unit
    def test_change_host_not_found(self, mock_profile):
        """Test change_host returns False when session not found."""
        mock_profile._get_session = MagicMock(return_value=None)

        status, reason = mock_profile.change_host('test-id', 'new.host.com')

        assert status is False
        assert 'does not exist' in reason

    @pytest.mark.unit
    def test_change_host_success(self, mock_profile):
        """Test change_host returns True on success."""
        mock_session = MagicMock()
        mock_profile._get_session = MagicMock(return_value=mock_session)
        mock_profile.save_profile = MagicMock()

        status, reason = mock_profile.change_host('test-id', 'new.host.com')

        assert status is True
        assert reason == ''
        assert mock_session.host == 'new.host.com'


class TestDBProfileSetNickname:
    """Tests for DBProfile.set_session_nickname method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.Session = MagicMock()
        return profile

    @pytest.mark.unit
    def test_set_nickname_not_found(self, mock_profile):
        """Test set_session_nickname returns False when session not found."""
        mock_profile._get_session = MagicMock(return_value=None)

        status, reason = mock_profile.set_session_nickname('test-id', 'NewNick')

        assert status is False
        assert 'does not exist' in reason

    @pytest.mark.unit
    def test_set_nickname_success(self, mock_profile):
        """Test set_session_nickname returns True on success."""
        mock_session = MagicMock()
        mock_profile._get_session = MagicMock(return_value=mock_session)
        mock_profile.save_profile = MagicMock()

        status, reason = mock_profile.set_session_nickname('test-id', 'NewNick')

        assert status is True
        assert reason == ''
        assert mock_session.nickname == 'NewNick'


class TestDBProfileVNCCredentials:
    """Tests for VNC credentials methods."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.Session = MagicMock()
        profile.VNCCredentials = MagicMock()
        return profile

    @pytest.mark.unit
    def test_set_vnc_credentials_not_found(self, mock_profile):
        """Test set_session_vnc_credentials returns False when session not found."""
        mock_profile._get_session = MagicMock(return_value=None)

        status, reason = mock_profile.set_session_vnc_credentials('test-id', {'password': 'test'})

        assert status is False
        assert 'does not exist' in reason

    @pytest.mark.unit
    def test_set_vnc_credentials_delete(self, mock_profile):
        """Test set_session_vnc_credentials deletes when credentials is None."""
        mock_session = MagicMock()
        mock_profile._get_session = MagicMock(return_value=mock_session)
        mock_profile.save_profile = MagicMock()

        mock_vnc_cred = MagicMock()
        mock_profile.VNCCredentials.query.filter_by.return_value.first.return_value = mock_vnc_cred

        status, reason = mock_profile.set_session_vnc_credentials('test-id', None)

        assert status is True
        mock_profile.db.session.delete.assert_called_once_with(mock_vnc_cred)

    @pytest.mark.unit
    def test_set_vnc_credentials_add(self, mock_profile):
        """Test set_session_vnc_credentials adds new credentials."""
        mock_session = MagicMock()
        mock_profile._get_session = MagicMock(return_value=mock_session)
        mock_profile.save_profile = MagicMock()

        # No existing credential
        mock_profile.VNCCredentials.query.filter_by.return_value.first.return_value = None

        status, reason = mock_profile.set_session_vnc_credentials('test-id', {'password': 'secret'})

        assert status is True
        mock_profile.db.session.add.assert_called_once()

    @pytest.mark.unit
    def test_get_vnc_credentials_not_found(self, mock_profile):
        """Test get_session_vnc_credentials returns False when session not found."""
        mock_profile._get_session = MagicMock(return_value=None)

        status, reason = mock_profile.get_session_vnc_credentials('test-id')

        assert status is False
        assert 'does not exist' in reason

    @pytest.mark.unit
    def test_get_vnc_credentials_no_credentials(self, mock_profile):
        """Test get_session_vnc_credentials returns empty when no credentials."""
        mock_session = MagicMock()
        mock_profile._get_session = MagicMock(return_value=mock_session)
        mock_profile.VNCCredentials.query.filter_by.return_value.first.return_value = None

        status, result = mock_profile.get_session_vnc_credentials('test-id')

        assert status is True
        assert result == ''

    @pytest.mark.unit
    def test_get_vnc_credentials_success(self, mock_profile):
        """Test get_session_vnc_credentials returns credentials."""
        mock_session = MagicMock()
        mock_profile._get_session = MagicMock(return_value=mock_session)

        credentials = {'password': 'secret'}
        encoded = base64.b64encode(json.dumps(credentials).encode('ascii')).decode('ascii')
        mock_vnc_cred = MagicMock()
        mock_vnc_cred.credentials = encoded
        mock_profile.VNCCredentials.query.filter_by.return_value.first.return_value = mock_vnc_cred

        status, result = mock_profile.get_session_vnc_credentials('test-id')

        assert status is True
        assert result == credentials


class TestDBProfileSendActivationEmail:
    """Tests for DBProfile.send_activation_email method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.User = MagicMock()
        profile.activation_cache = {}
        profile.resend_cooldown = {}
        profile.activation_email_body_template = '{username}{userid}{code}{expire_min}'
        return profile

    @pytest.mark.unit
    def test_send_activation_user_not_found(self, mock_profile):
        """Test send_activation_email aborts when user not found."""
        dbp_module = get_dbprofile_module()

        mock_profile.User.query.filter_by.return_value.first.return_value = None

        with patch.object(dbp_module, 'abort') as mock_abort:
            mock_abort.side_effect = Exception('abort')
            try:
                mock_profile.send_activation_email('nonexistent')
            except Exception:
                pass

            mock_abort.assert_called_once()
            assert mock_abort.call_args[0][0] == 403

    @pytest.mark.unit
    def test_send_activation_cooldown(self, mock_profile):
        """Test send_activation_email aborts when on cooldown."""
        dbp_module = get_dbprofile_module()

        mock_user = MagicMock()
        mock_user.id = 123
        mock_profile.User.query.filter_by.return_value.first.return_value = mock_user
        mock_profile.resend_cooldown['123'] = True

        with patch.object(dbp_module, 'abort') as mock_abort:
            mock_abort.side_effect = Exception('abort')
            try:
                mock_profile.send_activation_email('testuser')
            except Exception:
                pass

            mock_abort.assert_called_once()
            assert mock_abort.call_args[0][0] == 429

    @pytest.mark.unit
    def test_send_activation_success(self, mock_profile):
        """Test send_activation_email sends email successfully."""
        dbp_module = get_dbprofile_module()

        mock_user = MagicMock()
        mock_user.id = 456
        mock_user.email = 'test@mail.utoronto.ca'
        mock_profile.User.query.filter_by.return_value.first.return_value = mock_user

        with patch.object(dbp_module, 'send_email') as mock_send:
            result = mock_profile.send_activation_email('testuser')

            assert result is True
            mock_send.assert_called_once()
            assert '456' in mock_profile.activation_cache
            assert '456' in mock_profile.resend_cooldown


class TestDBProfileGetUser:
    """Tests for DBProfile.get_user method."""

    @pytest.fixture
    def mock_profile(self):
        """Create a mock DBProfile instance."""
        dbp_module = get_dbprofile_module()

        profile = dbp_module.DBProfile.__new__(dbp_module.DBProfile)
        profile.db = MagicMock()
        profile.User = MagicMock()
        return profile

    @pytest.mark.unit
    def test_get_user_not_logged_in(self, mock_profile):
        """Test get_user aborts when not logged in."""
        dbp_module = get_dbprofile_module()

        with patch.object(dbp_module, 'flask_session', {}), \
             patch.object(dbp_module, 'abort') as mock_abort:
            mock_abort.side_effect = Exception('abort')
            try:
                mock_profile.get_user()
            except Exception:
                pass

            mock_abort.assert_called_once_with(403, 'You are not logged in')

    @pytest.mark.unit
    def test_get_user_not_found(self, mock_profile):
        """Test get_user aborts when user not found."""
        dbp_module = get_dbprofile_module()

        mock_profile.User.query.filter_by.return_value.first.return_value = None

        with patch.object(dbp_module, 'flask_session', {'userid': 999}), \
             patch.object(dbp_module, 'abort') as mock_abort:
            mock_abort.side_effect = Exception('abort')
            try:
                mock_profile.get_user()
            except Exception:
                pass

            mock_abort.assert_called_once_with(403, 'Cannot find any matching record')

    @pytest.mark.unit
    def test_get_user_success(self, mock_profile):
        """Test get_user returns user on success."""
        dbp_module = get_dbprofile_module()

        mock_user = MagicMock()
        mock_profile.User.query.filter_by.return_value.first.return_value = mock_user

        with patch.object(dbp_module, 'flask_session', {'userid': 123}):
            result = mock_profile.get_user()

            assert result == mock_user
