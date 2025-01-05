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
import posixpath
from datetime import datetime
from pathlib import Path
from flask import request, abort, stream_with_context
from .common import create_connection
from .. import api, app
from ..codes import ConnectionType
import logging
logger = logging.getLogger(__name__)
UPLOAD_CHUNK_SIZE = 1024 * 1024

@api.route('/sftp_ls/<session_id>')
def sftp_ls(session_id):
    path = request.args.get('path')

    logger.debug("Sftp: Listing SFTP directory: %s for session %s", path, session_id)
    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        logger.error("Sftp: SFTP connection failed: %s", reason)
        abort(403, description=reason)

    status, cwd, file_list = sftp.ls(path)
    if status is False:
        logger.error("Sftp: Failed to list directory: %s", cwd)
        abort(400, description=cwd)

    result = {
        'cwd': cwd,
        'files': file_list
    }
    logger.info("Sftp: Directory listed successfully: %s", cwd)
    return json.dumps(result)


@api.route('/sftp_dl/<session_id>')
def sftp_dl(session_id):
    cwd = request.args.get('cwd')
    args_files = request.args.get('files')
    logger.debug("Sftp: Downloading files: %s from %s for session %s", args_files, cwd, session_id)
    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        logger.error("Sftp: SFTP connection failed: %s", reason)
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
        zip_name = posixpath.basename(cwd) + dt_str + '.zip'
        r.headers.set('Content-Disposition', 'attachment', filename=zip_name)
        logger.info("Sftp: Sending zip file: %s", zip_name)
    else:
        r = app.response_class(stream_with_context(sftp.dl_generator(files[0])), mimetype='application/octet-stream')
        r.headers.set('Content-Disposition', 'attachment', filename=files[0])
        r.headers.set('Content-Length', size)
        logger.info("Sftp: Sending file: %s", files[0])
    return r


@api.route('/sftp_rename/<session_id>', methods=['PATCH'])
def sftp_rename(session_id):
    cwd = request.json.get('cwd')
    old = request.json.get('old')
    new = request.json.get('new')
    logger.debug("Sftp: Renaming file from %s to %s in %s for session %s", old, new, cwd, session_id)
    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        logger.error("Sftp: SFTP connection failed: %s", reason)
        abort(403, description=reason)

    status, reason = sftp.rename(cwd, old, new)
    if not status:
        logger.error("Sftp: Rename failed: %s", reason)
        abort(400, reason)
    logger.info("Sftp: Rename successful from %s to %s", old, new)
    return 'success'


@api.route('/sftp_chmod/<session_id>', methods=['PATCH'])
def sftp_chmod(session_id):
    path = request.json.get('path')
    mode = request.json.get('mode')
    recursive = request.json.get('recursive')
    logger.debug("Sftp: Changing file mode for %s to %s, recursive: %s in session %s", path, mode, recursive, session_id)

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        logger.error("Sftp: SFTP connection failed: %s", reason)
        abort(403, description=reason)

    status, reason = sftp.chmod(path, mode, recursive)
    if not status:
        logger.error("Sftp: CHMOD failed: %s", reason)
        abort(400, reason)

    logger.info("Sftp: CHMOD successful for %s", path)
    return 'success'


@api.route('/sftp_mkdir/<session_id>', methods=['PUT'])
def sftp_mkdir(session_id):
    cwd = request.json.get('cwd')
    name = request.json.get('name')
    logger.debug("Sftp: Creating directory %s in %s for session %s", name, cwd, session_id)
    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        logger.error("Sftp: SFTP connection failed: %s", reason)
        abort(403, description=reason)

    status, reason = sftp.mkdir(cwd, name)
    if status is False:
        logger.error("Sftp: Directory creation failed: %s", reason)
        abort(400, description=reason)

    logger.info("Sftp: Directory created successfully: %s", name)
    return 'success'


@api.route('/sftp_ul/<session_id>', methods=['POST'])
def sftp_ul(session_id):
    cwd = request.headers.get('Cwd')
    # no need to use secure_filename because the user should be responsible for her/his input
    #  when not using the client
    relative_path = request.headers.get('Path')
    logger.debug("Sftp: Uploading file %s to %s for session %s", relative_path, cwd, session_id)

    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        logger.error("Sftp: SFTP connection failed: %s", reason)
        abort(403, description=reason)

    p = Path(relative_path)
    request_filename = p.name

    relative_dir_path = p.parent
    if str(relative_dir_path) != '.':
        cwd = posixpath.join(cwd, relative_dir_path)
        # TODO: check: will this ever fail?
        logger.debug("Sftp: Creating directories recursively for %s", cwd)
        sftp.exec_command_blocking(f'mkdir -p "{cwd}"')

    sftp.sftp.chdir(path=cwd)
    sftp_file = sftp.file(filename=request_filename)

    chunk = request.stream.read(UPLOAD_CHUNK_SIZE)
    while len(chunk) != 0:
        sftp_file.write(chunk)
        chunk = request.stream.read(UPLOAD_CHUNK_SIZE)

    sftp_file.close()
    logger.info("Sftp: File uploaded successfully: %s", request_filename)
    return 'success'


@api.route('/sftp_rm/<session_id>', methods=['POST'])
def sftp_rm(session_id):
    cwd = request.json.get('cwd')
    files = request.json.get('files')
    logger.debug("Sftp: Removing files %s from %s for session %s", files, cwd, session_id)
    sftp, reason = create_connection(session_id, ConnectionType.SFTP)
    if reason != '':
        logger.error("Sftp: SFTP connection failed: %s", reason)
        abort(403, description=reason)

    status, reason = sftp.rm(cwd, files)
    if not status:
        logger.error("Sftp: File removal failed: %s", reason)
        abort(400, description=reason)

    logger.info("Sftp: Files removed successfully from %s", cwd)
    return 'success'
