#  Copyright (c) 2021-2023 iCtrl Developers
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

from flask import request, abort, stream_with_context

from .common import create_connection
from .. import api, app, profiles
from ..codes import ICtrlStep, ICtrlError, ConnectionType
from ..utils import int_to_bytes
import logging
logger = logging.getLogger(__name__)

@api.route('/vnc', methods=['POST'])
def start_vnc():
    session_id = request.json.get('sessionID')
    load_check = request.json.get('loadCheck', True)
    load_credentials = request.json.get('loadCredentials', True)

    def generate():
        yield int_to_bytes(ICtrlStep.VNC.SSH_AUTH)
        vnc, reason = create_connection(session_id, ConnectionType.VNC)
        if reason != '':
            yield reason
            return

        yield int_to_bytes(ICtrlStep.VNC.CHECK_LOAD)
        if vnc.is_uoft() and load_check and vnc.is_load_high():
            yield int_to_bytes(ICtrlError.SSH.OVER_LOADED)
            return

        yield int_to_bytes(ICtrlStep.VNC.PARSE_PASSWD)
        # use5900: usually a RealVNC server listening on port 5900
        #  which we don't know how to parse the password
        use5900 = False
        credentials = None
        if not vnc.is_ecf():
            # in case we can read the password while the server is launched at port 5900
            # check whether 5900 is opened anyway
            use5900 = vnc.check_5900_open()

            # check if there are any save credentials
            if load_credentials:
                vnc_credential_status, credentials = profiles.get_session_vnc_credentials(session_id)
                if vnc_credential_status is False or credentials == "":
                    vnc_password_status, password = vnc.get_vnc_password()
                    if vnc_password_status:
                        credentials = {'password': password}
                    elif not use5900:
                        yield int_to_bytes(ICtrlError.VNC.PASSWD_MISSING)
                        return
            else:
                # remove any saved credentials
                profiles.set_session_vnc_credentials(session_id, None)

        yield int_to_bytes(ICtrlStep.VNC.LAUNCH_VNC)
        if vnc.is_ecf():
            vnc_port = 1000
        elif use5900:
            vnc_port = 5900
        else:
            status, vnc_port = vnc.launch_vnc()
            if not status:
                # TODO: handle the other failures
                yield int_to_bytes(ICtrlError.VNC.QUOTA_EXCEEDED)
                return

        yield int_to_bytes(ICtrlStep.VNC.CREATE_TUNNEL)
        ws_port = vnc.create_tunnel(vnc_port)

        yield int_to_bytes(ICtrlStep.VNC.DONE)
        result = {
            'port': ws_port,
            'credentials': credentials
        }
        yield json.dumps(result)

    return app.response_class(stream_with_context(generate()), mimetype='application/octet-stream')


@api.route('/vncpasswd', methods=['POST'])
def change_vncpasswd():
    logger.debug("in route /vncpasswd")
    session_id = request.json.get('session_id')

    vnc, reason = create_connection(session_id, ConnectionType.VNC)
    if reason != '':
        logger.error("create_connection() failed with status=", status)
        abort(403, description=reason)

    passwd = request.json.get('passwd')
    status, reason = vnc.reset_vnc_password(passwd)

    if not status:
        logger.error("reset_vnc_password() failed with status=%s", reason)
        abort(403, description=reason)

    return 'success'


@api.route('/vnc_reset', methods=['POST'])
def reset_vnc():
    session_id = request.json.get('session_id')

    vnc, reason = create_connection(session_id, ConnectionType.VNC)
    if reason != '':
        abort(403, description=reason)

    status, reason = vnc.remove_vnc_settings()
    if status is False:
        abort(403, description=reason)

    return 'success'


@api.route('/vnc_credentials', methods=['PUT'])
def vnc_credentials():
    session_id = request.json.get('session_id')
    credentials = request.json.get('credentials')

    status, reason = profiles.set_session_vnc_credentials(session_id, credentials)
    if status is False:
        abort(403, description=reason)

    return 'success'
