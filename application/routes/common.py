import os
from io import BytesIO

from flask import request, abort, send_file

from .. import app, profiles
from ..codes import ICtrlError, ConnectionType
from ..features.Connection import Connection
from ..features.Favicon import Favicon
from ..features.SFTP import SFTP
from ..features.Term import Term
from ..features.VNC import VNC
from ..paths import PRIVATE_KEY_PATH
from ..utils import int_to_bytes


def create_connection(session_id, conn_type):
    host, username, this_private_key_path = profiles.get_session_info(session_id)
    if host is None:
        abort(403, f'failed: session {session_id} does not exist')

    if conn_type == ConnectionType.GENERAL:
        conn = Connection()
    elif conn_type == ConnectionType.VNC:
        conn = VNC()
    elif conn_type == ConnectionType.TERM:
        conn = Term()
    elif conn_type == ConnectionType.SFTP:
        conn = SFTP()
    else:
        raise TypeError(f'Invalid type: {conn_type}')

    status, reason = conn.connect(host, username, key_filename=this_private_key_path)
    if status is False:
        if reason.startswith('[Errno 60]') \
                or reason.startswith('[Errno 64]') \
                or reason.startswith('[Errno 51]') \
                or reason == 'timed out':
            reason = int_to_bytes(ICtrlError.SSH.HOST_UNREACHABLE)
        else:
            print(reason)
            # TODO: return the other specific codes
            reason = int_to_bytes(ICtrlError.SSH.GENERAL)

    return conn, reason


def is_ecf(session_id):
    host, _, _ = profiles.get_session_info(session_id)
    return host.endswith('.ecf.utoronto.ca') or host.endswith('ecf.toronto.edu')


@app.route('/profiles')
def get_profiles():
    return profiles.query()


@app.route('/session', methods=['POST', 'PATCH', 'DELETE'])
def handle_session():
    if request.method == 'POST':
        host = request.json.get('host')
        username = request.json.get('username')
        password = request.json.get("password")

        conn = Connection()

        status, reason = conn.connect(host, username, password)
        if status is False:
            abort(403, reason)

        session_id = profiles.add_session(host, username)
        this_private_key_path = os.path.join(PRIVATE_KEY_PATH, session_id)
        status, reason = conn.save_keys(this_private_key_path)
        if status is False:
            abort(500, reason)

        return 'success'

    elif request.method == 'PATCH':
        session_id = request.json.get('session_id')
        host = request.json.get('host')

        status, reason = profiles.change_host(session_id, host)
        if not status:
            abort(403, reason)

        return 'success'

    elif request.method == 'DELETE':
        session_id = request.args.get('session_id')

        status, reason = profiles.delete_session(session_id)
        if not status:
            abort(403, reason)

        return 'success'
    else:
        abort(405)


@app.route('/exec_blocking', methods=['POST'])
def exec_blocking():
    session_id = request.json.get('session_id')
    cmd = request.json.get('cmd')

    conn, reason = create_connection(session_id, ConnectionType.GENERAL)
    if reason != '':
        abort(403, reason)

    status, _, stdout, stderr = conn.exec_command_blocking(cmd)
    if status is False:
        abort(500, 'exec failed')

    return '\n'.join(stdout) + '\n' + '\n'.join(stderr)


@app.route('/favicon/<feature>/<session_id>')
def generate_favicon(feature, session_id):
    host, _, _ = profiles.get_session_info(session_id)
    if host is None:
        abort(403, f'failed: session {session_id} does not exist')

    temp = BytesIO()
    icon = Favicon(host)
    if feature == 'vnc':
        icon.VNC(temp)
    elif feature == 'terminal':
        icon.console(temp)
    elif feature == 'fm':
        icon.file_manager(temp)
    else:
        abort(400, f'Invalid feature {feature}')

    temp.seek(0)
    return send_file(temp, mimetype='image/png')
