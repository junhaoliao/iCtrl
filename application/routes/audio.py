#  Copyright (c) 2022 iCtrl Developers
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

#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#
import json

from flask import request, abort

from .common import create_connection
from .. import api
from ..codes import ConnectionType
from ..features.Audio import AUDIO_PORT
import application

@api.route('/audio', methods=['POST'])
def start_audio():
    #TODO: Request recieved with body
    application.logger.debug("Received request to start audio with data: {}".format(request.json))
    session_id = request.json.get('session_id')
    audio, reason = create_connection(session_id, ConnectionType.AUDIO)
    if reason != '':
        application.logger.warning("Failed to create audio connection: {}".format(reason))
        abort(403, description=reason)

    status, reason = audio.launch_audio()
    if status is False:
        application.logger.error("Audio launch failed: {}".format(reason))
        abort(403, description=reason)

    result = {
        'port': AUDIO_PORT,
        'audio_id': audio.id
    }
    application.logger.info("Audio launched successfully with ID {} on port {}".format(audio.id, AUDIO_PORT))
    return json.dumps(result)
