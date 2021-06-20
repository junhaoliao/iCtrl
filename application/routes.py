import os
import threading

from flask import request, abort

from application import app, profiles
from application.Connection import Connection
from application.Terminal import Terminal
from application.paths import PRIVATE_KEY_PATH


def get_session_info():
    session_id = request.form.get('session_id')
    if session_id not in profiles['sessions']:
        abort(403, 'failed: session does not exist')
    host = profiles['sessions'][session_id]['host']
    username = profiles['sessions'][session_id]['username']
    this_private_key_path = os.path.join(PRIVATE_KEY_PATH, session_id)
    return host, username, this_private_key_path


@app.route('/profiles')
def get_profiles():
    return profiles.query()


@app.route('/session', methods=['POST'])
def new_session():
    host = request.form.get('host')
    username = request.form.get('username')
    password = request.form.get("password")

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


@app.route('/exec_blocking', methods=['POST'])
def exec_blocking():
    host, username, this_private_key_path = get_session_info()

    cmd = request.form.get('cmd')

    conn = Connection()
    status, reason = conn.connect(host, username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    # TODO: test this
    status, _, stdout, stderr = conn.exec_command_blocking(cmd)
    if status is False:
        abort(500, 'exec failed')

    return '\n'.join(stdout) + '\n'.join(stderr)


@app.route('/terminal', methods=['POST'])
def start_terminal():
    host, username, this_private_key_path = get_session_info()

    term = Terminal()
    status, reason = term.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    return term.id


# @app.route('/vnc', methods=['POST'])
# def start_vnc():
#     host, username, this_private_key_path = get_session_info()
#
