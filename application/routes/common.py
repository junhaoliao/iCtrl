import json
from io import BytesIO

from flask import request, abort, send_file

from .. import api, profiles
from ..codes import ICtrlError, ConnectionType
from ..features.Connection import Connection
from ..features.Favicon import Favicon
from ..features.SFTP import SFTP
from ..features.Term import Term
from ..features.VNC import VNC
from ..utils import int_to_bytes


def create_connection(session_id, conn_type):
    host, username, this_private_key_path, this_private_key_str = profiles.get_session_info(session_id)
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

    status, reason = conn.connect(host, username,
                                  key_filename=this_private_key_path, private_key_str=this_private_key_str)
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
    host, _, _, _ = profiles.get_session_info(session_id)
    return host.endswith('.ecf.utoronto.ca') or host.endswith('ecf.toronto.edu')


@api.route('/profiles')
def get_profiles():
    return profiles.query()


@api.route('/session', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def handle_session():
    if request.method == 'GET':
        session_id = request.args.get('id')
        host, username, _, _ = profiles.get_session_info(session_id)

        return json.dumps({
            'host': host,
            'username': username
        })
    elif request.method == 'POST':
        host = request.json.get('host')
        username = request.json.get('username')
        # FIXME: password should be optional
        password = request.json.get("password")

        conn = Connection()

        status, reason = conn.connect(host, username, password=password)
        if status is False:
            abort(403, reason)

        # FIXME: password should be optional: only pass 'conn' if password is given
        status, reason = profiles.add_session(host, username, conn)
        if status is False:
            abort(500, reason)

        return 'success'

    elif request.method == 'PATCH':
        session_id = request.json.get('session_id')
        host = request.json.get('host')
        domain = request.json.get('domain')

        # terminate old sessions with the best effort
        # noinspection PyBroadException
        try:
            conn, _ = create_connection(session_id, ConnectionType.GENERAL)
            conn.exec_command_blocking('vncserver -kill ":*"')
        except Exception:
            pass

        if domain is  None:
            # find the domain when the domain is not specified
            full_host_name, _, _, _ = profiles.get_session_info(session_id)
            domain = full_host_name[full_host_name.find('.'):]

        host += domain

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


@api.route('/exec_blocking', methods=['POST'])
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


@api.route('/favicon/<feature>/<session_id>')
def generate_favicon(feature, session_id):
    host, _, _, _ = profiles.get_session_info(session_id)
    if host is None:
        abort(403, f'failed: session {session_id} does not exist')

    icon = Favicon.generate(host, feature)

    return send_file(icon, mimetype='image/png')
