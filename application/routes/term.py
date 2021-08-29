import json

from flask import request, abort

from .common import create_connection
from .. import app
from ..codes import ICtrlStep, ConnectionType
from ..features.Term import terminal_connections, TERMINAL_PORT
from ..utils import int_to_bytes


# FIXME: store term_id is cookie-based Flask 'session'

@app.route('/terminal', methods=['POST'])
def start_terminal():
    session_id = request.json.get('session_id')

    def generate():
        yield int_to_bytes(ICtrlStep.Term.SSH_AUTH)

        term, reason = create_connection(session_id, ConnectionType.TERM)
        if reason != '':
            yield reason
            return

        yield int_to_bytes(ICtrlStep.Term.CHECK_LOAD)

        yield int_to_bytes(ICtrlStep.Term.LAUNCH_SHELL)
        status, reason = term.launch_shell()
        if status is False:
            abort(403, description=reason)

        yield int_to_bytes(ICtrlStep.Term.DONE)
        result = {
            'port': TERMINAL_PORT,
            'term_id': term.id
        }
        yield json.dumps(result)

    return app.response_class(generate(), mimetype='application/octet-stream')


@app.route('/terminal_resize', methods=['PATCH'])
def resize_terminal():
    term_id = request.json.get('term_id')
    if term_id not in terminal_connections:
        abort(403, description='invalid term_id')

    width = request.json.get('w')
    height = request.json.get('h')

    term = terminal_connections[term_id]
    status, reason = term.resize(width, height)
    if status is False:
        abort(403, description=reason)

    return 'success'
