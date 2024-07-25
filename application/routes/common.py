#  Copyright (c) 2021-2022 iCtrl Developers
# 
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.

import json
import threading

from flask import request, abort

from .. import api, profiles
from ..codes import ICtrlError, ConnectionType
from ..features.Audio import Audio
from ..features.Connection import Connection
from ..features.SFTP import SFTP
from ..features.Term import Term
from ..features.VNC import VNC
from ..utils import int_to_bytes
import application

def create_connection(session_id, conn_type):
    application.logger.debug(f"Common: Attempting to create connection: session_id={session_id}, conn_type={conn_type}")
    host, username, this_private_key_path, this_private_key_str, _ = profiles.get_session_info(session_id)
    if host is None:
        application.logger.warning(f"Common: Session not found: {session_id}")
        abort(403, f'Fail: session {session_id} does not exist')

    if conn_type == ConnectionType.GENERAL:
        conn = Connection()
    elif conn_type == ConnectionType.VNC:
        conn = VNC()
    elif conn_type == ConnectionType.TERM:
        conn = Term()
    elif conn_type == ConnectionType.SFTP:
        conn = SFTP()
    elif conn_type == ConnectionType.AUDIO:
        conn = Audio()
    else:
        application.logger.error(f"Common: Invalid connection type requested: {conn_type}")
        raise TypeError(f'Invalid type: {conn_type}')

    status, reason = conn.connect(host, username,
                                  key_filename=this_private_key_path, private_key_str=this_private_key_str)
    if status is False:
        application.logger.error(f"Common: Connection failed: {reason}")
        if reason.startswith('[Errno 60]') \
                or reason.startswith('[Errno 64]') \
                or reason.startswith('[Errno 51]') \
                or reason == 'timed out':
            reason = int_to_bytes(ICtrlError.SSH.HOST_UNREACHABLE)
        elif "encountered RSA key, expected OPENSSH key" in reason:
            reason = int_to_bytes(ICtrlError.SSH.AUTH_WRONG)
        else:
            print(reason)
            # TODO: return the other specific codes
            reason = int_to_bytes(ICtrlError.SSH.GENERAL)

    return conn, reason


@api.route('/profiles')
def get_profiles():
    application.logger.info("Common: Fetching all profiles")
    return profiles.query()


@api.route('/session', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def handle_session():
    application.logger.debug(f"Common: Session operation: {request.method}")
    if request.method == 'GET':
        session_id = request.args.get('id')
        host, username, _, _, nickname = profiles.get_session_info(session_id)

        return json.dumps({
            'host': host,
            'username': username,
            'nickname': nickname
        })
    elif request.method == 'POST':
        host = request.json.get('host')
        username = request.json.get('username')
        # FIXME: password should be optional
        password = request.json.get("password")
        application.logger.debug("Common: Creating new session")
        conn = Connection()

        status, reason = conn.connect(host, username, password=password)
        if status is False:
            application.logger.warning(f"Common: Failed to create session: {reason}")
            abort(403, reason)

        # FIXME: password should be optional: only pass 'conn' if password is given
        status, reason = profiles.add_session(host, username, conn)
        if status is False:
            application.logger.error("Common: Failed to save session info")
            abort(500, reason)

        return 'success'

    elif request.method == 'PATCH':
        session_id = request.json.get('session_id')
        host = request.json.get('host')
        domain = request.json.get('domain')
        nickname = request.json.get('nickname')

        if nickname is not None:
            # only update nickname
            application.logger.info(f"Common: Updating nickname for session {session_id}")
            status, reason = profiles.set_session_nickname(session_id, nickname)
            if not status:
                abort(400, reason)
        else:
            application.logger.info("Common: Terminating old session")
            # terminate old sessions with best efforts
            # noinspection PyBroadException
            try:
                kill_cmd_list = [
                    'vncserver -kill ":*"',
                    'killall -q -w xvfb-run Xtigervnc'
                ]
                conn, _ = create_connection(session_id, ConnectionType.GENERAL)
                threading.Thread(target=conn.exec_command_blocking, args=[';'.join(kill_cmd_list)]).start()
            except Exception:
                pass

            if domain is None:
                # find the domain when the domain is not specified
                full_host_name, _, _, _, _ = profiles.get_session_info(session_id)
                if full_host_name is None:
                    abort(400, f'failed: session {session_id} does not exist')
                domain = full_host_name[full_host_name.find('.'):]

            host += domain

            status, reason = profiles.change_host(session_id, host)
            if not status:
                abort(403, reason)

        return 'success'

    elif request.method == 'DELETE':
        session_id = request.args.get('session_id')
        application.logger.info(f"Common: Deleting session {session_id}")
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
    large = request.json.get('large', False)
    application.logger.debug("Common: Executing blocking command")
    conn, reason = create_connection(session_id, ConnectionType.GENERAL)
    if reason != '':
        abort(403, reason)

    result: str
    if large:
        result = conn.exec_command_blocking_large(cmd)
    else:
        status, _, stdout, stderr = conn.exec_command_blocking(cmd)
        if status is False:
            application.logger.error("Common: Command execution failed")
            abort(500, 'exec failed')
        result = '\n'.join(stdout) + '\n' + '\n'.join(stderr)

    return result
