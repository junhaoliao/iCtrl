import json

from flask import request, abort, stream_with_context

from .common import create_connection
from .. import api, app
from ..codes import ICtrlStep, ConnectionType, ICtrlError
from ..features.Term import terminal_connections, TERMINAL_PORT
from ..utils import int_to_bytes


# FIXME: store term_id is cookie-based Flask 'session'

@api.route('/terminal', methods=['POST'])
def start_terminal():
    session_id = request.json.get('session_id')
    no_load_check = request.json.get('no_load_check')

    def generate():
        yield int_to_bytes(ICtrlStep.Term.SSH_AUTH)

        term, reason = create_connection(session_id, ConnectionType.TERM)
        if reason != '':
            yield reason
            return

        yield int_to_bytes(ICtrlStep.Term.CHECK_LOAD)
        if term.is_uoft() and no_load_check is False and term.is_load_high():
            yield int_to_bytes(ICtrlError.SSH.OVER_LOADED)
            return

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

    return app.response_class(stream_with_context(generate()), mimetype='application/octet-stream')


@api.route('/terminal_resize', methods=['PATCH'])
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
