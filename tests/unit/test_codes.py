"""
Unit tests for application/codes.py

These tests don't require Docker services.
"""

import pytest
from application.codes import (
    ConnectionType,
    VNCError,
    SSHError,
    VNCStep,
    TermStep,
    ICtrlError,
    ICtrlStep,
    STEP_DONE,
    ERROR_GENERAL,
)


class TestConnectionType:
    """Tests for ConnectionType enum."""

    @pytest.mark.unit
    def test_values(self):
        assert ConnectionType.GENERAL == 1
        assert ConnectionType.VNC == 2
        assert ConnectionType.TERM == 3
        assert ConnectionType.SFTP == 4
        assert ConnectionType.AUDIO == 5

    @pytest.mark.unit
    def test_unique(self):
        """All values should be unique."""
        values = [ct.value for ct in ConnectionType]
        assert len(values) == len(set(values))


class TestVNCStep:
    """Tests for VNCStep enum."""

    @pytest.mark.unit
    def test_values(self):
        assert VNCStep.SSH_AUTH == 0
        assert VNCStep.CHECK_LOAD == 1
        assert VNCStep.PARSE_PASSWD == 2
        assert VNCStep.LAUNCH_VNC == 3
        assert VNCStep.CREATE_TUNNEL == 4
        assert VNCStep.DONE == 31

    @pytest.mark.unit
    def test_done_equals_step_done(self):
        assert VNCStep.DONE == STEP_DONE


class TestTermStep:
    """Tests for TermStep enum."""

    @pytest.mark.unit
    def test_values(self):
        assert TermStep.SSH_AUTH == 0
        assert TermStep.CHECK_LOAD == 1
        assert TermStep.LAUNCH_SHELL == 2
        assert TermStep.DONE == 31

    @pytest.mark.unit
    def test_done_equals_step_done(self):
        assert TermStep.DONE == STEP_DONE


class TestVNCError:
    """Tests for VNCError enum."""

    @pytest.mark.unit
    def test_values(self):
        assert VNCError.GENERAL == 120
        assert VNCError.PASSWD_MISSING == 121
        assert VNCError.QUOTA_EXCEEDED == 122

    @pytest.mark.unit
    def test_greater_than_error_general(self):
        """VNC errors should be ERROR_GENERAL + 20 and above."""
        assert VNCError.GENERAL == ERROR_GENERAL + 20


class TestSSHError:
    """Tests for SSHError enum."""

    @pytest.mark.unit
    def test_values(self):
        assert SSHError.GENERAL == 200
        assert SSHError.HOST_UNREACHABLE == 201
        assert SSHError.AUTH_MISSING == 202
        assert SSHError.AUTH_WRONG == 203
        assert SSHError.OVER_LOADED == 204


class TestICtrlError:
    """Tests for ICtrlError class."""

    @pytest.mark.unit
    def test_vnc_alias(self):
        assert ICtrlError.VNC == VNCError
        assert ICtrlError.VNC.GENERAL == 120

    @pytest.mark.unit
    def test_ssh_alias(self):
        assert ICtrlError.SSH == SSHError
        assert ICtrlError.SSH.GENERAL == 200


class TestICtrlStep:
    """Tests for ICtrlStep class."""

    @pytest.mark.unit
    def test_vnc_alias(self):
        assert ICtrlStep.VNC == VNCStep
        assert ICtrlStep.VNC.DONE == 31

    @pytest.mark.unit
    def test_term_alias(self):
        assert ICtrlStep.Term == TermStep
        assert ICtrlStep.Term.DONE == 31


class TestConstants:
    """Tests for module-level constants."""

    @pytest.mark.unit
    def test_step_done(self):
        assert STEP_DONE == 31

    @pytest.mark.unit
    def test_error_general(self):
        assert ERROR_GENERAL == 100
