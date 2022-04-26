/*
 * Copyright (c) 2022 iCtrl Developers
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to
 *  deal in the Software without restriction, including without limitation the
 *  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 *  sell copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 *  IN THE SOFTWARE.
 */

import axios from 'axios';
import PCMPlayer from './PCMPlayer';

export const launch_audio = (vncsd, sessionID) => {
  const player = new PCMPlayer({
    format: 's16le',
    numberOfChannels: 2,
    sampleRate: 44100,
    flushInterval: 100,
  });
  axios.post('/api/audio', {
    session_id: sessionID,
  }).then((response) => {
    const {port, audio_id} = response.data;
    const socket = new WebSocket(
        `${process.env.REACT_APP_DOMAIN_NAME ? 'wss' : 'ws'}
://${process.env.REACT_APP_DOMAIN_NAME || '127.0.0.1'}:${port}/${audio_id}`);
    socket.binaryType = 'arraybuffer';

    socket.onopen = (_) => {
      vncsd.setState({
        enableAudio: true,
      });
    };
    socket.onmessage = (ev) => {
      player.feed(ev.data);
    };
    socket.onclose = (_) => {
      player.destroy();
    };

    vncsd.audioSocket = socket;
  }).catch((error) => {
    console.log(error);
  });
};