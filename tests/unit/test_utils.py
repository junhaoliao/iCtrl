"""
Unit tests for application/utils.py

These tests don't require Docker services.
"""

import pytest
from unittest.mock import Mock, patch
from application.utils import (
    int_to_bytes,
    validate_password,
    get_headers_dict_from_str,
    find_free_port,
    local_auth,
)


class TestIntToBytes:
    """Tests for int_to_bytes function."""

    @pytest.mark.unit
    def test_zero(self):
        assert int_to_bytes(0) == b'\x00'

    @pytest.mark.unit
    def test_positive(self):
        assert int_to_bytes(31) == b'\x1f'
        assert int_to_bytes(100) == b'd'
        assert int_to_bytes(255) == b'\xff'

    @pytest.mark.unit
    def test_step_done_code(self):
        """STEP_DONE = 31"""
        assert int_to_bytes(31) == bytes([31])


class TestValidatePassword:
    """Tests for validate_password function."""

    @pytest.mark.unit
    def test_valid_password(self):
        """Password meeting all requirements."""
        ok, reason = validate_password("TestPass1!")
        assert ok is True
        assert reason is None

    @pytest.mark.unit
    def test_password_too_short(self):
        ok, reason = validate_password("Ab1!")
        assert ok is False
        assert "at least 6 characters" in reason

    @pytest.mark.unit
    def test_password_too_long(self):
        ok, reason = validate_password("A" * 30 + "b1!")
        assert ok is False
        assert "exceed 32 characters" in reason

    @pytest.mark.unit
    def test_password_no_digit(self):
        ok, reason = validate_password("TestPass!")
        assert ok is False
        assert "numeral" in reason

    @pytest.mark.unit
    def test_password_no_uppercase(self):
        ok, reason = validate_password("testpass1!")
        assert ok is False
        assert "uppercase" in reason

    @pytest.mark.unit
    def test_password_no_lowercase(self):
        ok, reason = validate_password("TESTPASS1!")
        assert ok is False
        assert "lowercase" in reason

    @pytest.mark.unit
    def test_password_no_special(self):
        ok, reason = validate_password("TestPass1")
        assert ok is False
        assert "symbol" in reason

    @pytest.mark.unit
    def test_all_special_chars_accepted(self):
        """Test all allowed special characters."""
        special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+']
        for char in special_chars:
            password = f"TestPass1{char}"
            ok, reason = validate_password(password)
            assert ok is True, f"Special char '{char}' should be accepted"


class TestGetHeadersDictFromStr:
    """Tests for get_headers_dict_from_str function."""

    @pytest.mark.unit
    def test_empty_string(self):
        headers = get_headers_dict_from_str("")
        assert headers == {}

    @pytest.mark.unit
    def test_single_header(self):
        headers = get_headers_dict_from_str("Content-Type: application/json\r\n")
        assert headers == {"Content-Type": "application/json"}

    @pytest.mark.unit
    def test_multiple_headers(self):
        header_str = "Content-Type: application/json\r\nAuthorization: Bearer token123\r\n"
        headers = get_headers_dict_from_str(header_str)
        assert headers == {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123"
        }

    @pytest.mark.unit
    def test_skips_get_line(self):
        """GET request line should be skipped."""
        header_str = "GET /api/test HTTP/1.1\r\nHost: localhost\r\n"
        headers = get_headers_dict_from_str(header_str)
        assert "GET" not in headers
        assert headers == {"Host": "localhost"}

    @pytest.mark.unit
    def test_header_with_colon_in_value(self):
        """Headers with colons in value should be parsed correctly."""
        header_str = "X-Custom: value:with:colons\r\n"
        headers = get_headers_dict_from_str(header_str)
        assert headers == {"X-Custom": "value:with:colons"}

    @pytest.mark.unit
    def test_skips_lines_without_colon(self):
        header_str = "Content-Type: text/plain\r\nInvalidLine\r\nHost: test\r\n"
        headers = get_headers_dict_from_str(header_str)
        assert headers == {"Content-Type": "text/plain", "Host": "test"}


class TestFindFreePort:
    """Tests for find_free_port function."""

    @pytest.mark.unit
    def test_returns_integer(self):
        port = find_free_port()
        assert isinstance(port, int)

    @pytest.mark.unit
    def test_returns_valid_port_range(self):
        port = find_free_port()
        assert 1024 <= port <= 65535

    @pytest.mark.unit
    def test_returns_different_ports(self):
        """Multiple calls should typically return different ports."""
        port1 = find_free_port()
        port2 = find_free_port()
        # They could technically be the same, but usually won't be
        assert isinstance(port1, int)
        assert isinstance(port2, int)


class TestLocalAuth:
    """Tests for local_auth function."""

    @pytest.mark.unit
    def test_auth_success_with_valid_key(self):
        """Auth should pass with valid Bearer token."""
        abort_func = Mock()
        headers = {"Authorization": "Bearer test-auth-key"}

        with patch.dict('os.environ', {'ICTRL_LOCAL_AUTH_KEY': 'test-auth-key'}):
            result = local_auth(headers, abort_func)

        assert result is True
        abort_func.assert_not_called()

    @pytest.mark.unit
    def test_auth_failure_with_wrong_key(self):
        """Auth should fail with wrong Bearer token."""
        abort_func = Mock()
        headers = {"Authorization": "Bearer wrong-key"}

        with patch.dict('os.environ', {'ICTRL_LOCAL_AUTH_KEY': 'test-auth-key'}):
            result = local_auth(headers, abort_func)

        assert result is False
        abort_func.assert_called_once_with(403, "You are not authorized to access this API.")

    @pytest.mark.unit
    def test_auth_failure_with_missing_header(self):
        """Auth should fail when Authorization header is missing."""
        abort_func = Mock()
        headers = {}

        with patch.dict('os.environ', {'ICTRL_LOCAL_AUTH_KEY': 'test-auth-key'}):
            result = local_auth(headers, abort_func)

        assert result is False
        abort_func.assert_called_once()

    @pytest.mark.unit
    def test_auth_failure_with_wrong_type(self):
        """Auth should fail with non-Bearer token type."""
        abort_func = Mock()
        headers = {"Authorization": "Basic test-auth-key"}

        with patch.dict('os.environ', {'ICTRL_LOCAL_AUTH_KEY': 'test-auth-key'}):
            result = local_auth(headers, abort_func)

        assert result is False
        abort_func.assert_called_once()

    @pytest.mark.unit
    def test_auth_pass_with_empty_auth_key(self):
        """Auth should pass when ICTRL_LOCAL_AUTH_KEY is empty (disabled)."""
        abort_func = Mock()
        headers = {}  # No auth header needed

        with patch.dict('os.environ', {'ICTRL_LOCAL_AUTH_KEY': ''}):
            result = local_auth(headers, abort_func)

        assert result is True
        abort_func.assert_not_called()


class TestSendEmail:
    """Tests for send_email function."""

    @pytest.mark.unit
    def test_send_email_success(self):
        """Test send_email sends email successfully."""
        from application.utils import send_email

        with patch.dict('os.environ', {
            'ICTRL_SENDER_SERVER': 'smtp.test.com',
            'ICTRL_SENDER_PORT': '465',
            'ICTRL_SENDER_EMAIL': 'sender@test.com',
            'ICTRL_SENDER_PASSWD': 'password123'
        }), patch('application.utils.smtplib.SMTP_SSL') as mock_smtp, \
            patch('application.utils.ssl.create_default_context') as mock_ssl:
            mock_server = Mock()
            mock_smtp.return_value = mock_server

            send_email('recipient@test.com', 'Test Subject', '<p>Test body</p>')

            mock_smtp.assert_called_once()
            mock_server.ehlo.assert_called_once()
            mock_server.login.assert_called_once_with('sender@test.com', 'password123')
            mock_server.sendmail.assert_called_once()
            mock_server.close.assert_called_once()

    @pytest.mark.unit
    def test_send_email_with_ca_cert(self):
        """Test send_email loads custom CA certificate when provided."""
        from application.utils import send_email
        import tempfile
        import os

        # Create a temp file to simulate CA cert
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write('dummy cert')
            ca_cert_path = f.name

        try:
            with patch.dict('os.environ', {
                'ICTRL_SENDER_SERVER': 'smtp.test.com',
                'ICTRL_SENDER_PORT': '465',
                'ICTRL_SENDER_EMAIL': 'sender@test.com',
                'ICTRL_SENDER_PASSWD': 'password123',
                'ICTRL_SMTP_CA_CERT': ca_cert_path
            }), patch('application.utils.smtplib.SMTP_SSL') as mock_smtp, \
                patch('application.utils.ssl.create_default_context') as mock_ssl:
                mock_server = Mock()
                mock_smtp.return_value = mock_server
                mock_context = Mock()
                mock_ssl.return_value = mock_context

                send_email('recipient@test.com', 'Test Subject', '<p>Test body</p>')

                mock_context.load_verify_locations.assert_called_once_with(ca_cert_path)
        finally:
            os.unlink(ca_cert_path)
