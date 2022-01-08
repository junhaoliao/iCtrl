import json
import re

from flask import request, abort, stream_with_context

from .common import create_connection, is_ecf
from .. import api, app
from ..codes import ICtrlStep, ICtrlError, ConnectionType
from ..utils import int_to_bytes


@api.route('/vnc', methods=['POST'])
def start_vnc():
    session_id = request.json.get('session_id')
    no_load_check = request.json.get('no_load_check')

    def generate():
        yield int_to_bytes(ICtrlStep.VNC.SSH_AUTH)
        vnc, reason = create_connection(session_id, ConnectionType.VNC)
        if reason != '':
            yield reason
            return

        yield int_to_bytes(ICtrlStep.VNC.CHECK_LOAD)
        if vnc.is_uoft() and no_load_check is False:
            status, _, stdout, _ = vnc.exec_command_blocking('uptime')
            if status is False:
                abort(500, 'exec failed')

            output = stdout.readlines()[0].split(',')

            user_count, = re.findall(r'\d+', output[2])
            load1, = re.findall(r"\d+\.\d+", output[3])

            if int(user_count) > 0 or float(load1) > 0.2:
                yield int_to_bytes(ICtrlError.SSH.OVER_LOADED)
                return

        yield int_to_bytes(ICtrlStep.VNC.PARSE_PASSWD)
        # use5900: usually a RealVNC server listening on port 5900
        #  which we don't know how to parse the password
        use5900 = False
        session_is_ecf = is_ecf(session_id)
        if session_is_ecf:
            password = None
        else:
            status, password = vnc.get_vnc_password()
            if not status:
                use5900 = vnc.check_5900_open()
                if use5900:
                    password = None
                else:
                    yield int_to_bytes(ICtrlError.VNC.PASSWD_MISSING)
                    return

        yield int_to_bytes(ICtrlStep.VNC.LAUNCH_VNC)
        if session_is_ecf:
            vnc_port = 1000
        elif use5900:
            vnc_port = 5900
        else:
            # FIXME: handle the case when the vnc server can't be launched
            vnc_port = vnc.launch_vnc()

        yield int_to_bytes(ICtrlStep.VNC.CREATE_TUNNEL)
        ws_port = vnc.create_tunnel(vnc_port)

        yield int_to_bytes(ICtrlStep.VNC.DONE)
        result = {
            'port': ws_port,
            'passwd': password
        }
        yield json.dumps(result)

    return app.response_class(stream_with_context(generate()), mimetype='application/octet-stream')


@api.route('/vncpasswd', methods=['POST'])
def change_vncpasswd():
    session_id = request.json.get('session_id')

    vnc, reason = create_connection(session_id, ConnectionType.VNC)
    if reason != '':
        abort(403, description=reason)

    passwd = request.json.get('passwd')
    status, reason = vnc.reset_vnc_password(passwd)
    if not status:
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
