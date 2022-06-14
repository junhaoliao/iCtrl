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

import React from 'react';
import {IconButton} from '@mui/material';
import {VolumeUp} from '@mui/icons-material';

export default class ICtrlVoiceButton extends React.Component {
  constructor(props) {
    super(props);

    this.sources = [
      '/ictrl-voice/ictrl-slow.mp3',
      '/ictrl-voice/ictrl-robot.mp3',
      '/ictrl-voice/ictrl-teleport.mp3',
    ];
    this.colors = [
      'grey',
      'black',
      'black',
    ];
    this.nextVoiceIdx = 0;

    this.state = {
      buttonDisabled: false,
      buttonColor: this.colors[0],
      buttonBackground: null,
    };
  }

  _showNextButton = () => {
    this.setState({
      buttonDisabled: false,
      buttonColor: this.colors[this.nextVoiceIdx],
      buttonBackground: (this.nextVoiceIdx + 1 ===
              this.sources.length) &&
          'conic-gradient(red, yellow, lime, aqua, blue, magenta, red)',
    });
  };

  handlePlayICtrlVoice = () => {
    const audio = new Audio(this.sources[this.nextVoiceIdx]);

    audio.play();
    this.nextVoiceIdx = (this.nextVoiceIdx + 1) %
        this.sources.length;
    this.setState({
      buttonDisabled: true,
    });

    if (this.nextVoiceIdx !== 0) {
      setTimeout(this._showNextButton, 300);
    } else {
      audio.onended = this._showNextButton;
    }
  };

  render() {
    const {
      buttonDisabled,
      buttonColor,
      buttonBackground,
    } = this.state;

    return (
        <IconButton
            disabled={buttonDisabled}
            style={{
              alignSelf: 'center',
              color: buttonColor,
              background: buttonBackground,
            }}
            onClick={this.handlePlayICtrlVoice}>
          <VolumeUp/>
        </IconButton>
    );
  }
}
