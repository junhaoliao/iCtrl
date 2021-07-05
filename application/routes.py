import json
import os
from datetime import datetime

from flask import request, abort

from application import app, profiles
from application.Connection import Connection
from application.SFTP import SFTP
from application.Terminal import Terminal
from application.VNC import VNC
from application.paths import PRIVATE_KEY_PATH

UPLOAD_CHUNK_SIZE = 1024 * 1024


def get_session_info(session_id):
    if session_id not in profiles['sessions']:
        abort(403, f'failed: session {session_id} does not exist')
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
    session_id = request.form.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

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
    session_id = request.form.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

    term = Terminal()
    status, reason = term.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    return term.id


@app.route('/vnc', methods=['POST'])
def start_vnc():
    session_id = request.json.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

    vnc = VNC()
    status, reason = vnc.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    status, password = vnc.get_vnc_password()
    if not status:
        abort(403, description='VNC password missing')

    port = vnc.launch_web_vnc()
    result = {
        'port': port,
        'passwd': password
    }
    return json.dumps(result)


@app.route('/vncpasswd', methods=['POST'])
def change_vncpasswd():
    session_id = request.form.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

    vnc = VNC()
    status, reason = vnc.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    passwd = request.form.get('passwd')
    status, reason = vnc.reset_vnc_password(passwd)
    if not status:
        abort(403, description=reason)

    return 'success'


@app.route('/sftp_ls/<session_id>')
def sftp_ls(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    path = request.args.get('path')
    status, cwd, file_list = sftp.ls(path)
    if status is False:
        abort(400, description=cwd)

    result = {
        'status': status,
        'cwd': cwd,
        'files': file_list
    }
    return json.dumps(result)


@app.route('/sftp_dl/<session_id>')
def sftp_dl(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    cwd = request.args.get('cwd')
    files = json.loads(request.args.get('files'))

    sftp.sftp.chdir(cwd)

    zip_mode = True
    size = 0
    if len(files) == 1:
        is_reg, size = sftp.reg_size(files[0])
        zip_mode = not is_reg

    if zip_mode:
        r = app.response_class(sftp.zip_generator(cwd, files), mimetype='application/zip')
        dt_str = datetime.now().strftime('_%Y%m%d_%H%M%S')
        zip_name = os.path.basename(cwd) + dt_str + '.zip'
        r.headers.set('Content-Disposition', 'attachment', filename=zip_name)
    else:
        r = app.response_class(sftp.dl_generator(files[0]), mimetype='application/octet-stream')
        r.headers.set('Content-Disposition', 'attachment', filename=files[0])
        r.headers.set('Content-Length', size)

    return r


@app.route('/sftp_rename/<session_id>', methods=['PATCH'])
def sftp_rename(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    cwd = request.json.get('cwd')
    old = request.json.get('old')
    new = request.json.get('new')

    status, reason = sftp.rename(cwd, old, new)
    if not status:
        abort(400, reason)

    return 'success'


@app.route('/sftp_ul/<session_id>', methods=['POST'])
def sftp_ul(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    path = request.headers.get('Path')
    # no need to use secure_filename because the user should be responsible for her/his input
    #  when not using the client
    request_filename = request.headers.get('Filename')
    if request_filename == '':
        abort(400, 'Empty file handle')

    sftp.sftp.chdir(path=path)
    sftp_file = sftp.file(filename=request_filename)

    chunk = request.stream.read(UPLOAD_CHUNK_SIZE)
    while len(chunk) != 0:
        sftp_file.write(chunk)
        chunk = request.stream.read(UPLOAD_CHUNK_SIZE)

    sftp_file.close()

    return 'success'


@app.route('/sftp_rm/<session_id>', methods=['POST'])
def sftp_rm(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    cwd = request.json.get('cwd')
    files = request.json.get('files')

    status, reason = sftp.rm(cwd, files)
    if not status:
        abort(400, description=reason)

    return 'success'
