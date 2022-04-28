/*
 * Copyright (c) 2022 iCtrl Developers
 * ​Copyright (c) 2018 Samir Das <cse.samir@gmail.com>
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

// original project: https://github.com/samirkumardas/pcm-player
// modification:
// 1. Performance improvement
// 2. Fix a bug where audio is out of sync occasionally

export default class PCMPlayer {
  static maxValue = {
    's8': 128,
    's16le': 32768,
    's32le': 2147483648,
    'f32le': 1,
  };

  static arrayType = {
    's8': Int8Array,
    's16le': Int16Array,
    's32le': Int32Array,
    'f32le': Float32Array,
  };

  static defaultOptions = {
    numberOfChannels: 2,
    sampleRate: 44100,
    format: 's16le',
    flushInterval: 100,
  };

  options;    // player options
  audioCtx;   // audioCtx in browser
  samples;    // audio samples (buffer with producer being 'this.feed' and consumer being 'this.flush')
  dateStart;  // real timer for playback sync
  startTime;  // timer for playback sync
  flushCbHandle; // flush callback handle

  constructor(options) {
    // set up options for the player
    this.options = {...PCMPlayer.defaultOptions, ...options};

    // audio samples (buffer with producer being 'this.feed' and consumer being 'this.flush')
    this.samples = [];

    // create audio context
    this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    this.audioCtx.resume(); // in macOS players, the audio context does not autoplay

    // real timer for playback sync
    this.dateStart = Date.now();

    // timer for playback sync
    this.startTime = this.audioCtx.currentTime;

    // set up callback to flush the audio every "flushInterval" milliseconds
    this.flushCbHandle = setInterval(this.flush, this.options.flushInterval);
  }

  feed = (buffer) => {
    const data = new PCMPlayer.arrayType[this.options.format](buffer);
    // get the max value for conversion into a float of range [-1.0, 1.0]
    const maxValue = PCMPlayer.maxValue[this.options.format];
    for (const d of data) {
      // convert into a float of range [-1.0, 1.0] and push into this.samples
      this.samples.push(d / maxValue);
    }
  };

  flush = () => {
    // no need to flush if no sample is available
    if (this.samples.length === 0) {
      return;
    }

    // create a new audio source
    const bufferSource = this.audioCtx.createBufferSource();

    // how many frames are available in this source
    const numberOfFrames = this.samples.length / this.options.numberOfChannels;

    // create a multichannel buffer to be used in the buffer source
    const audioBuffer = this.audioCtx.createBuffer(
        this.options.numberOfChannels,
        numberOfFrames,
        this.options.sampleRate);

    let sampleIdx = 0;
    for (let channel = 0; channel < this.options.numberOfChannels; channel++) {
      // get buffer for the current channel
      const channelBuffer = audioBuffer.getChannelData(channel);

      // the sample starting indexing should be an offset equal to the channel index
      sampleIdx = channel;
      // copy sample data into channel buffer
      for (let frameIdx = 0; frameIdx < numberOfFrames; frameIdx++) {
        channelBuffer[frameIdx] = this.samples[sampleIdx];
        sampleIdx += this.options.numberOfChannels;
      }
    }

    // sync playback time with the context
    // TODO: test on FireFox due to reduced precision for timing attack prevention
    //  https://developer.mozilla.org/en-US/docs/Web/API/BaseAudioContext/currentTime
    if (this.startTime < this.audioCtx.currentTime - 0.05) {
      console.log('hardware time sync', this.startTime,
          this.audioCtx.currentTime);
      this.startTime = this.audioCtx.currentTime;
    }

    // set up the buffer in the buffer source
    bufferSource.buffer = audioBuffer;

    // route the buffer source to destination (speaker)
    bufferSource.connect(this.audioCtx.destination);

    // play this chunk of samples at startTime
    bufferSource.start(this.startTime);

    // when the next chunk of samples should be play
    this.startTime += audioBuffer.duration;

    // sync playback time with the actual clock
    const dateTotalDuration = (Date.now() - this.dateStart) / 1000;
    if (this.startTime - dateTotalDuration > this.options.flushInterval * 3 /
        1000) {
      console.log('real time sync', this.startTime, dateTotalDuration);
      this.startTime = dateTotalDuration;
    }
    this.samples = [];
  };

  destroy = () => {
    if (this.flushCbHandle) {
      clearInterval(this.flushCbHandle);
    }
    this.flushCbHandle = null;

    this.options = null;

    this.audioCtx.close();
    this.audioCtx = null;

    this.dateStart = null;
    this.startTime = null;

    this.samples = null;
  };
}
