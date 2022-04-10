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
import os
from datetime import datetime
from pathlib import Path

from flask import request, abort, stream_with_context

from .common import create_connection
from .. import api, app
from ..codes import ConnectionType

UPLOAD_CHUNK_SIZE = 1024 * 1024


@api.route('/sftp_ls/<session_id>')
def sftp_ls(session_id):
    path = request.args.get('path')

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        abort(403, description=reason)

    status, cwd, file_list = sftp.ls(path)
    if status is False:
        abort(400, description=cwd)

    result = {
        'cwd': cwd,
        'files': file_list
    }
    return json.dumps(result)


@api.route('/sftp_dl/<session_id>')
def sftp_dl(session_id):
    cwd = request.args.get('cwd')
    args_files = request.args.get('files')

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        abort(403, description=reason)

    files = json.loads(args_files)

    sftp.sftp.chdir(cwd)

    zip_mode = True
    size = 0
    if len(files) == 1:
        is_reg, size = sftp.reg_size(files[0])
        zip_mode = not is_reg

    if zip_mode:
        r = app.response_class(stream_with_context(sftp.zip_generator(cwd, files)), mimetype='application/zip')
        dt_str = datetime.now().strftime('_%Y%m%d_%H%M%S')
        zip_name = os.path.basename(cwd) + dt_str + '.zip'
        r.headers.set('Content-Disposition', 'attachment', filename=zip_name)
    else:
        r = app.response_class(stream_with_context(sftp.dl_generator(files[0])), mimetype='application/octet-stream')
        r.headers.set('Content-Disposition', 'attachment', filename=files[0])
        r.headers.set('Content-Length', size)

    return r


@api.route('/sftp_rename/<session_id>', methods=['PATCH'])
def sftp_rename(session_id):
    cwd = request.json.get('cwd')
    old = request.json.get('old')
    new = request.json.get('new')

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        abort(403, description=reason)

    status, reason = sftp.rename(cwd, old, new)
    if not status:
        abort(400, reason)

    return 'success'


@api.route('/sftp_chmod/<session_id>', methods=['PATCH'])
def sftp_chmod(session_id):
    path = request.json.get('path')
    mode = request.json.get('mode')
    recursive = request.json.get('recursive')

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        abort(403, description=reason)

    status, reason = sftp.chmod(path, mode, recursive)
    if not status:
        abort(400, reason)

    return 'success'


@api.route('/sftp_mkdir/<session_id>', methods=['PUT'])
def sftp_mkdir(session_id):
    cwd = request.json.get('cwd')
    name = request.json.get('name')

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        abort(403, description=reason)

    status, reason = sftp.mkdir(cwd, name)
    if status is False:
        abort(400, description=reason)

    return 'success'


@api.route('/sftp_ul/<session_id>', methods=['POST'])
def sftp_ul(session_id):
    cwd = request.headers.get('Cwd')
    # no need to use secure_filename because the user should be responsible for her/his input
    #  when not using the client
    relative_path = request.headers.get('Path')

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        abort(403, description=reason)

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


@api.route('/sftp_rm/<session_id>', methods=['POST'])
def sftp_rm(session_id):
    cwd = request.json.get('cwd')
    files = request.json.get('files')

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        abort(403, description=reason)

    status, reason = sftp.rm(cwd, files)
    if not status:
        abort(400, description=reason)

    return 'success'
