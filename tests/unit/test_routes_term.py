"""
Unit tests for routes/term.py.

Tests the terminal route handlers.
"""

import sys
import json
import pytest
from unittest.mock import patch, MagicMock


def get_term_routes_module():
    """Get the routes/term module from sys.modules."""
    if 'application' not in sys.modules:
        if len(sys.argv) < 2 or not sys.argv[1].isdigit():
            sys.argv = ['pytest', '5000', 'test-auth-key']
        import application
    return sys.modules['application.routes.term']


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


class TestStartTerminal:
    """Tests for /api/terminal endpoint."""

    def test_start_terminal_success(self, client):
        """POST /api/terminal creates terminal session and returns port info."""
        term_routes = get_term_routes_module()
        codes = get_codes_module()

        with patch.object(term_routes, 'create_connection') as mock_create, \
             patch.object(term_routes, 'TERMINAL_PORT', 12345):

            mock_term = MagicMock()
            mock_term.id = 'test-term-id'
            mock_term.supports_load_check.return_value = False  # Skip load check
            mock_term.launch_shell.return_value = (True, '')
            mock_create.return_value = (mock_term, '')

            response = client.post(
                '/api/terminal',
                json={'sessionID': 'test-session', 'loadCheck': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Response is streaming, collect all chunks
            data = response.data

            # Should contain step codes and JSON result
            assert len(data) > 0
            # Check for DONE marker (ICtrlStep.Term.DONE = 31)
            assert codes.ICtrlStep.Term.DONE in data

    def test_start_terminal_connection_failed(self, client):
        """POST /api/terminal returns error on connection failure."""
        term_routes = get_term_routes_module()
        codes = get_codes_module()

        with patch.object(term_routes, 'create_connection') as mock_create:
            mock_term = MagicMock()
            mock_create.return_value = (mock_term, b'connection error')

            response = client.post(
                '/api/terminal',
                json={'sessionID': 'test-session'},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Should contain the error in the response
            assert b'connection error' in response.data

    def test_start_terminal_overloaded(self, client):
        """POST /api/terminal returns overload error when server is loaded."""
        term_routes = get_term_routes_module()
        codes = get_codes_module()

        with patch.object(term_routes, 'create_connection') as mock_create:
            mock_term = MagicMock()
            mock_term.supports_load_check.return_value = True  # Enable load check
            mock_term.is_load_high.return_value = True
            mock_create.return_value = (mock_term, '')

            response = client.post(
                '/api/terminal',
                json={'sessionID': 'test-session', 'loadCheck': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Should contain OVER_LOADED error code
            data = response.data
            assert codes.ICtrlError.SSH.OVER_LOADED in data

    def test_start_terminal_skip_load_check(self, client):
        """POST /api/terminal skips load check when loadCheck=False."""
        term_routes = get_term_routes_module()
        codes = get_codes_module()

        with patch.object(term_routes, 'create_connection') as mock_create, \
             patch.object(term_routes, 'TERMINAL_PORT', 12345):

            mock_term = MagicMock()
            mock_term.id = 'test-term-id'
            mock_term.supports_load_check.return_value = True  # Would be checked
            mock_term.is_load_high.return_value = True  # Would fail if checked
            mock_term.launch_shell.return_value = (True, '')
            mock_create.return_value = (mock_term, '')

            response = client.post(
                '/api/terminal',
                json={'sessionID': 'test-session', 'loadCheck': False},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            # Should succeed because load check was skipped
            assert codes.ICtrlStep.Term.DONE in response.data
            # supports_load_check should not have been called when loadCheck=False
            mock_term.supports_load_check.assert_not_called()
            mock_term.is_load_high.assert_not_called()

    def test_start_terminal_no_load_check_support(self, client):
        """POST /api/terminal skips load check for servers that don't support it."""
        term_routes = get_term_routes_module()
        codes = get_codes_module()

        with patch.object(term_routes, 'create_connection') as mock_create, \
             patch.object(term_routes, 'TERMINAL_PORT', 12345):

            mock_term = MagicMock()
            mock_term.id = 'test-term-id'
            mock_term.supports_load_check.return_value = False  # Doesn't support load check
            mock_term.launch_shell.return_value = (True, '')
            mock_create.return_value = (mock_term, '')

            response = client.post(
                '/api/terminal',
                json={'sessionID': 'test-session', 'loadCheck': True},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert codes.ICtrlStep.Term.DONE in response.data
            # is_load_high should not have been called because server doesn't support load check
            mock_term.is_load_high.assert_not_called()


class TestResizeTerminal:
    """Tests for /api/terminal_resize endpoint."""

    def test_resize_terminal_success(self, client):
        """PATCH /api/terminal_resize resizes terminal successfully."""
        term_routes = get_term_routes_module()

        mock_term = MagicMock()
        mock_term.resize.return_value = (True, '')

        with patch.dict(term_routes.TERM_CONNECTIONS, {'test-term-id': mock_term}):
            response = client.patch(
                '/api/terminal_resize',
                json={'term_id': 'test-term-id', 'w': 120, 'h': 40},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 200
            assert response.data == b'success'
            mock_term.resize.assert_called_once_with(120, 40)

    def test_resize_terminal_invalid_id(self, client):
        """PATCH /api/terminal_resize returns 403 for invalid term_id."""
        term_routes = get_term_routes_module()

        with patch.dict(term_routes.TERM_CONNECTIONS, {}, clear=True):
            response = client.patch(
                '/api/terminal_resize',
                json={'term_id': 'nonexistent-id', 'w': 80, 'h': 24},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403

    def test_resize_terminal_failed(self, client):
        """PATCH /api/terminal_resize returns 403 if resize fails."""
        term_routes = get_term_routes_module()

        mock_term = MagicMock()
        mock_term.resize.return_value = (False, 'Resize failed')

        with patch.dict(term_routes.TERM_CONNECTIONS, {'test-term-id': mock_term}):
            response = client.patch(
                '/api/terminal_resize',
                json={'term_id': 'test-term-id', 'w': 80, 'h': 24},
                headers={"Authorization": "Bearer test-auth-key"}
            )

            assert response.status_code == 403
