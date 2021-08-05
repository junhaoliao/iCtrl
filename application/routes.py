import json
import os
from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import request, abort, send_file

from application import app, profiles
from application.Connection import Connection
from application.Favicon import Favicon
from application.SFTP import SFTP
from application.Term import Term, terminal_connections, TERMINAL_PORT
from application.VNC import VNC
from application.codes import ICtrlStep, ICtrlError
from application.paths import PRIVATE_KEY_PATH
from application.utils import int_to_bytes

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
        if session_id not in profiles['sessions']:
            abort(403, f'failed: session {session_id} does not exist')

        host = request.json.get('host')
        profiles.change_host(session_id, host)

        return 'success'
    elif request.method == 'DELETE':
        session_id = request.args.get('session_id')
        if session_id not in profiles['sessions']:
            abort(403, f'failed: session {session_id} does not exist')

        profiles.delete_session(session_id)
        return 'success'
    else:
        abort(405)


@app.route('/exec_blocking', methods=['POST'])
def exec_blocking():
    session_id = request.json.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

    cmd = request.json.get('cmd')

    conn = Connection()
    status, reason = conn.connect(host, username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    status, _, stdout, stderr = conn.exec_command_blocking(cmd)
    if status is False:
        abort(500, 'exec failed')

    return '\n'.join(stdout) + '\n'.join(stderr)


@app.route('/terminal', methods=['POST'])
def start_terminal():
    session_id = request.json.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

    term = Term()
    status, reason = term.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    result = {
        'port': TERMINAL_PORT,
        'term_id': term.id
    }
    return json.dumps(result)


@app.route('/terminal_resize', methods=['PATCH'])
def resize_terminal():
    session_id = request.json.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

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


@app.route('/vnc', methods=['POST'])
def start_vnc():
    session_id = request.json.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)
    is_ecf = host.endswith('.ecf.utoronto.ca') or host.endswith('ecf.toronto.edu')

    def generate():
        yield int_to_bytes(ICtrlStep.VNC.SSH_AUTH)
        vnc = VNC()
        status, reason = vnc.connect(host=host, username=username, key_filename=this_private_key_path)
        if status is False:
            if reason.startswith('[Errno 60]'):
                yield int_to_bytes(ICtrlError.SSH.HOST_UNREACHABLE)
            else:
                # TODO: return the other specific codes
                yield int_to_bytes(ICtrlError.SSH.GENERAL)
            return

        yield int_to_bytes(ICtrlStep.VNC.CHECK_LOAD)

        yield int_to_bytes(ICtrlStep.VNC.PARSE_PASSWD)
        if is_ecf:
            password = None
        else:
            status, password = vnc.get_vnc_password()
            if not status:
                yield int_to_bytes(ICtrlError.VNC.PASSWD_MISSING)
                return

        yield int_to_bytes(ICtrlStep.VNC.LAUNCH_VNC)
        if is_ecf:
            vnc_port = 1000
        else:
            vnc_port = vnc.launch_vnc()

        yield int_to_bytes(ICtrlStep.VNC.CREATE_TUNNEL)
        ws_port = vnc.create_tunnel(vnc_port)

        yield int_to_bytes(ICtrlStep.VNC.DONE)
        result = {
            'port': ws_port,
            'passwd': password
        }
        yield json.dumps(result)

    return app.response_class(generate(), mimetype='application/octet-stream')


@app.route('/vncpasswd', methods=['POST'])
def change_vncpasswd():
    session_id = request.json.get('session_id')
    host, username, this_private_key_path = get_session_info(session_id)

    vnc = VNC()
    status, reason = vnc.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    passwd = request.json.get('passwd')
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


@app.route('/sftp_chmod/<session_id>', methods=['PATCH'])
def sftp_chmod(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    path = request.json.get('path')
    mode = request.json.get('mode')
    recursive = request.json.get('recursive')

    status, reason = sftp.chmod(path, mode, recursive)
    if not status:
        abort(400, reason)

    return 'success'


@app.route('/sftp_mkdir/<session_id>', methods=['PUT'])
def sftp_mkdir(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    cwd = request.json.get('cwd')
    name = request.json.get('name')

    status, reason = sftp.mkdir(cwd, name)
    if status is False:
        abort(400, description=reason)

    return 'success'


@app.route('/sftp_ul/<session_id>', methods=['POST'])
def sftp_ul(session_id):
    host, username, this_private_key_path = get_session_info(session_id)

    sftp = SFTP()
    status, reason = sftp.connect(host=host, username=username, key_filename=this_private_key_path)
    if status is False:
        abort(403, description=reason)

    cwd = request.headers.get('Cwd')

    # no need to use secure_filename because the user should be responsible for her/his input
    #  when not using the client
    relative_path = request.headers.get('Path')

    p = Path(relative_path)
    request_filename = p.name

    relative_dir_path = p.parent
    if str(relative_dir_path) != '.':
        cwd = os.path.join(cwd, relative_dir_path)
        # TODO: check: will this ever fail?
        sftp.exec_command_blocking(f'mkdir -p "{cwd}"')

    sftp.sftp.chdir(path=cwd)
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


@app.route('/favicon/<feature>/<session_id>')
def generate_favicon(feature, session_id):
    host, _, _ = get_session_info(session_id)

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
