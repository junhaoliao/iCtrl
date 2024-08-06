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

import os
import threading
import uuid
from typing import Optional

import paramiko
import zlib
from SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket
from werkzeug.serving import generate_adhoc_ssl_context

from .Connection import Connection
from .. import app
from ..utils import find_free_port, get_headers_dict_from_str, local_auth
import logging.config

logger = logging.getLogger(__name__)

AUDIO_CONNECTIONS = {}

FFMPEG_LOAD_TIME = 4  # unit: seconds
TRY_FFMPEG_MAX_COUNT = 3
AUDIO_BUFFER_SIZE = 20480


class Audio(Connection):
    def __init__(self):
        self.id = None
        self.transport: Optional[paramiko.Transport] = None
        self.remote_port = 0

        super().__init__()

    def __del__(self):
        print('Audio::__del__')
        if self.remote_port != 0:
            self.transport.cancel_port_forward('127.0.0.1', self.remote_port)
        if self.transport is not None:
            self.transport.close()

        super().__del__()

    def connect(self, *args, **kwargs):
        logger.debug("Audio: Establishing Audio connection")
        return super().connect(*args, **kwargs)

    def launch_audio(self):
        try:
            logger.debug("Audio: Launching Audio connection. Forwarding request to 127.0.0.1, port 0.")
            self.transport = self.client.get_transport()
            self.remote_port = self.transport.request_port_forward('127.0.0.1', 0)
        except Exception as e:
            logger.warning("Audio: exception raised during launch audio: {}".format(e))
            return False, str(e)

        self.id = uuid.uuid4().hex
        AUDIO_CONNECTIONS[self.id] = self

        return True, self.id


class AudioWebSocket(WebSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio: Optional[Audio] = None
        self.module_id = None

    def handleConnected(self):
        headers = self.headerbuffer.decode('utf-8')
        headers = get_headers_dict_from_str(headers)
        if not local_auth(headers=headers, abort_func=self.close):
            # local auth failure
            logger.warning("AudioWebSocket: Local Authentication Failure")
            return

        audio_id = self.request.path[1:]
        if audio_id not in AUDIO_CONNECTIONS:
            logger.warning(f'AudioWebSocket: Requested audio_id={audio_id} does not exist.')
            self.close()
            return

        self.audio = AUDIO_CONNECTIONS[audio_id]

        sink_name = 'remote_' + self.audio.username

        # only load module if the module is not loaded for the current user
        load_module_command = f'sh -c \'pactl list modules | while IFS=" " read -r name module_number; do if test ' \
                              f'"$name" == "Module"; then while IFS=" " read -r sub_name value; do if test $sub_name ' \
                              f'== "Argument:"; then if test "$value" == "sink_name={sink_name}"; then echo "${{' \
                              f'module_number#*#}}"; fi; break; fi; done; fi; done;\'| grep . || pactl load-module ' \
                              f'module-null-sink sink_name={sink_name} '
        exit_status, _, stdout, _ = self.audio.exec_command_blocking(load_module_command)
        if exit_status != 0:
            logger.warning(f'AudioWebSocket: audio_id={audio_id}: unable to load pactl module-null-sink sink_name={sink_name}')
            return
        load_module_stdout_lines = stdout.readlines()
        logger.debug("AudioWebSocket: Load Module: {}".format(load_module_stdout_lines))
        self.module_id = int(load_module_stdout_lines[0])

        keep_launching_ffmpeg = True

        def ffmpeg_launcher():
            logger.debug("AudioWebSocket: ffmpeg_launcher thread started")
            # TODO: support requesting audio format from the client
            launch_ffmpeg_command = f'killall ffmpeg; ffmpeg -f pulse -i "{sink_name}.monitor" ' \
                                    f'-ac 2 -acodec pcm_s16le -ar 44100 -f s16le "tcp://127.0.0.1:{self.audio.remote_port}"'
            # keep launching if the connection is not accepted in the writer() below
            while keep_launching_ffmpeg:
                logger.debug(f"AudioWebSocket: Launch ffmpeg: {launch_ffmpeg_command}")
                _, ffmpeg_stdout, _ = self.audio.client.exec_command(launch_ffmpeg_command)
                ffmpeg_stdout.channel.recv_exit_status()
                # if `ffmpeg` launches successfully, `ffmpeg_stdout.channel.recv_exit_status` should not return
            logger.debug("AudioWebSocket: ffmpeg_launcher thread ended")

        ffmpeg_launcher_thread = threading.Thread(target=ffmpeg_launcher)

        def writer():
            logger.debug("AudioWebSocket: writer thread started")
            channel = self.audio.transport.accept(FFMPEG_LOAD_TIME * TRY_FFMPEG_MAX_COUNT)

            nonlocal keep_launching_ffmpeg
            keep_launching_ffmpeg = False

            if channel is None:
                ffmpeg_launcher_thread.join()
                logger.error("AudioWebSocket:handleConnected: Unable to launch audio socket on the remote target. ")
                # raise ConnectionError("AudioWebSocket:handleConnected: Unable to launch audio socket on the remote "
                #                       "target. ")

            # use a buffer to reduce transfer frequency
            buffer = b''
            while True:
                data = channel.recv(AUDIO_BUFFER_SIZE)
                if not data:
                    logger.debug("AudioWebSocket: Close audio socket connection")
                    self.close()
                    break
                buffer += data
                if len(buffer) >= AUDIO_BUFFER_SIZE:
                    compressed = zlib.compress(buffer, level=4)
                    logger.debug(f"AudioWebSocket: Send compressed message of size {len(compressed)}")
                    self.sendMessage(compressed)
                    # print(len(compressed) / len(buffer) * 100)
                    buffer = b''
            logger.debug("AudioWebSocket: write thread ended")

        writer_thread = threading.Thread(target=writer)

        writer_thread.start()
        ffmpeg_launcher_thread.start()

    def handleClose(self):
        if self.module_id is not None:
            # unload the module before leaving
            logger.debug(f"AudioWebSocket: Unload module {self.module_id}")
            self.audio.client.exec_command(f'pactl unload-module {self.module_id}')

        logger.debug(f"AudioWebSocket: End audio socket {self.audio.id} connection")
        del AUDIO_CONNECTIONS[self.audio.id]
        del self.audio


# if the Flask 'app' is in debug mode, all code will be re-run (which means they will run twice) after app.run()
# since the ws server will bind to the port, we should only run it once
# if we are in debug mode, run the server in the second round
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    AUDIO_PORT = find_free_port()
    # print("AUDIO_PORT =", AUDIO_PORT)
    logger.debug("Audio: Audio port {}".format(AUDIO_PORT))

    if os.environ.get('SSL_CERT_PATH') is None:
        logger.debug("Audio: SSL Certification Path not set. Generating self-signing certificate")
        # no certificate provided, generate self-signing certificate
        audio_server = SimpleSSLWebSocketServer('127.0.0.1', AUDIO_PORT, AudioWebSocket,
                                                ssl_context=generate_adhoc_ssl_context())
    else:
        logger.debug("Audio: SSL Certification Path exists")
        import ssl

        audio_server = SimpleSSLWebSocketServer('0.0.0.0', AUDIO_PORT, AudioWebSocket,
                                                certfile=os.environ.get('SSL_CERT_PATH'),
                                                keyfile=os.environ.get('SSL_KEY_PATH'),
                                                version=ssl.PROTOCOL_TLS)

    threading.Thread(target=audio_server.serveforever, daemon=True).start()
