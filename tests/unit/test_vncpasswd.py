"""
Unit tests for features/vncpasswd.py.

Tests the VNC password obfuscation and decryption functions.
"""

import tempfile
import os
import pytest
from unittest.mock import patch, MagicMock

# Import the module
from application.features.vncpasswd import (
    obfuscate_password,
    decrypt_passwd,
    vncpasswd,
    vncpasswd2plain,
    read_password,
)


class TestObfuscatePassword:
    """Tests for obfuscate_password function."""

    @pytest.mark.unit
    def test_short_password(self):
        """Test password shorter than 8 chars is padded."""
        result = obfuscate_password("short")
        assert len(result) == 8  # DES block size

    @pytest.mark.unit
    def test_eight_char_password(self):
        """Test password exactly 8 chars."""
        result = obfuscate_password("12345678")
        assert len(result) == 8

    @pytest.mark.unit
    def test_long_password_truncated(self):
        """Test password longer than 8 chars is truncated."""
        result1 = obfuscate_password("12345678")
        result2 = obfuscate_password("12345678extracharacters")
        assert result1 == result2

    @pytest.mark.unit
    def test_empty_password(self):
        """Test empty password is padded."""
        result = obfuscate_password("")
        assert len(result) == 8


class TestDecryptPasswd:
    """Tests for decrypt_passwd function."""

    @pytest.mark.unit
    def test_round_trip(self):
        """Test obfuscate then decrypt returns original."""
        password = "test123"
        obfuscated = obfuscate_password(password)
        decrypted = decrypt_passwd(obfuscated)
        assert decrypted == password

    @pytest.mark.unit
    def test_round_trip_8_char(self):
        """Test full 8 character password round trip."""
        password = "password"
        obfuscated = obfuscate_password(password)
        decrypted = decrypt_passwd(obfuscated)
        assert decrypted == password

    @pytest.mark.unit
    def test_decrypt_strips_null(self):
        """Test null bytes are stripped from decrypted password."""
        password = "abc"
        obfuscated = obfuscate_password(password)
        decrypted = decrypt_passwd(obfuscated)
        # Should not have trailing null bytes
        assert decrypted == "abc"
        assert '\0' not in decrypted


class TestVncpasswd:
    """Tests for vncpasswd function."""

    @pytest.mark.unit
    def test_write_password_file(self):
        """Test writing password to file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            passwd_path = f.name

        try:
            result = vncpasswd(passwd_path, password="mypasswd")

            # Check the file was written
            with open(passwd_path, 'rb') as f:
                content = f.read()

            assert len(content) == 8
            assert result == content
        finally:
            os.unlink(passwd_path)

    @pytest.mark.unit
    def test_write_password_obfuscated(self):
        """Test password is properly obfuscated when written."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            passwd_path = f.name

        try:
            password = "secret"
            vncpasswd(passwd_path, password=password)

            # Verify by reading back and decrypting
            with open(passwd_path, 'rb') as f:
                obfuscated = f.read()

            decrypted = decrypt_passwd(obfuscated)
            assert decrypted == password
        finally:
            os.unlink(passwd_path)

    @pytest.mark.unit
    def test_write_password_calls_read_when_none(self):
        """Test vncpasswd calls read_password when password is None."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            passwd_path = f.name

        try:
            mock_obfuscated = b'12345678'
            with patch('application.features.vncpasswd.read_password', return_value=mock_obfuscated) as mock_read:
                result = vncpasswd(passwd_path, password=None)

                mock_read.assert_called_once()
                assert result == mock_obfuscated
        finally:
            os.unlink(passwd_path)


class TestVncpasswd2plain:
    """Tests for vncpasswd2plain function."""

    @pytest.mark.unit
    def test_read_password_from_file(self):
        """Test reading and decrypting password from file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            passwd_path = f.name

        try:
            # Write an obfuscated password
            password = "testpwd"
            obfuscated = obfuscate_password(password)
            with open(passwd_path, 'wb') as f:
                f.write(obfuscated)

            # Read it back
            result = vncpasswd2plain(passwd_path)
            assert result == password
        finally:
            os.unlink(passwd_path)


class TestReadPassword:
    """Tests for read_password function."""

    @pytest.mark.unit
    def test_empty_password_exits(self):
        """Test empty password causes exit."""
        mock_getpass = MagicMock(return_value='')
        with patch.dict('sys.modules', {'getpass': MagicMock(getpass=mock_getpass)}):
            # Re-import to get the patched version
            with patch('getpass.getpass', return_value=''):
                with pytest.raises(SystemExit) as exc_info:
                    read_password()
                assert exc_info.value.code == 1

    @pytest.mark.unit
    def test_short_password_prompts_again(self):
        """Test password shorter than 6 chars prompts again."""
        # First: short password, Second: valid password, Third: verify
        with patch('getpass.getpass', side_effect=['abc', 'valid123', 'valid123']):
            with patch('builtins.print') as mock_print:
                result = read_password()
                mock_print.assert_any_call('Password must be at least 6 characters - try again')

    @pytest.mark.unit
    def test_mismatched_passwords_prompts_again(self):
        """Test mismatched passwords prompts again."""
        # First: valid password, Second: wrong verify, Third: valid password, Fourth: correct verify
        with patch('getpass.getpass', side_effect=['valid123', 'wrong', 'valid123', 'valid123']):
            with patch('builtins.print') as mock_print:
                result = read_password()
                mock_print.assert_any_call("Passwords don't match - try again")

    @pytest.mark.unit
    def test_valid_password_returns_obfuscated(self):
        """Test valid matching passwords returns obfuscated result."""
        password = 'validpassword'
        with patch('getpass.getpass', side_effect=[password, password]):
            result = read_password()

            # Result should be obfuscated password
            decrypted = decrypt_passwd(result)
            assert decrypted == password[:8]  # VNC passwords are max 8 chars
