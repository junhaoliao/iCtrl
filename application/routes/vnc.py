import json

from flask import request, abort, stream_with_context

from .common import create_connection, is_ecf
from .. import app
from ..codes import ICtrlStep, ICtrlError, ConnectionType
from ..utils import int_to_bytes


@app.route('/vnc', methods=['POST'])
def start_vnc():
    session_id = request.json.get('session_id')

    def generate():
        yield int_to_bytes(ICtrlStep.VNC.SSH_AUTH)
        vnc, reason = create_connection(session_id, ConnectionType.VNC)
        if reason != '':
            yield reason
            return

        yield int_to_bytes(ICtrlStep.VNC.CHECK_LOAD)

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


@app.route('/vncpasswd', methods=['POST'])
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


@app.route('/vnc_reset', methods=['POST'])
def reset_vnc():
    session_id = request.json.get('session_id')

    vnc, reason = create_connection(session_id, ConnectionType.VNC)
    if reason != '':
        abort(403, description=reason)

    status, reason = vnc.remove_vnc_settings()
    if status is False:
        abort(403, description=reason)

    return 'success'
