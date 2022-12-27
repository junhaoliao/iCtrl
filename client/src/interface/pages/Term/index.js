/*
 * Copyright (c) 2021-2022 iCtrl Developers
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
import 'xterm/css/xterm.css';
import {sendKey, termConnect} from '../../../actions/term';
import {TermSteps} from '../../components/Loading/steps';
import Loading from '../../components/Loading';
import Toolbar from '../../components/Toolbar';
import {isMobile} from '../../../actions/utils';
import {updateTitleAndIcon} from '../../../actions/common';
import BackgroundLetterAvatar from '../../components/BackgroundLetterAvatar';
import {COLOR_TERM_VIEWER} from '../../constants';

export default class Term extends React.Component {
  constructor(props) {
    super(props);

    this.feature = document.title = 'Terminal';

    const {match: {params}} = this.props;
    this.session_id = params.session_id;
    this.loadCheck = new URLSearchParams(window.location.search).get(
        'load-check') !== 'false';

    this.resize_timeout = null;

    this.ctrlKey = false;
    this.shiftKey = false;
    this.metaKey = false;
    this.altKey = false;

    this.touchStartDelta = 0;

    this.state = {
      sessionNickname: '',
      scaleLevel: 1,
      loading: true,
      currentStep: -1,
      authentication: null,
      isOverloaded: false,
    };
  }

  handleToolbarSendKey = (key, down) => {
    this.term.focus();

    switch (key) {
      case 'Ctrl':
        this.ctrlKey = down;
        break;
      case 'Alt':
        this.altKey = down;
        break;
      case 'Shift':
        this.shiftKey = down;
        break;
      case '⌘':
        this.metaKey = down;
        break;

      case 'Tab':
        sendKey(this, {key: 'Tab', keyCode: 9});
        break;
      case 'Esc':
        sendKey(this, {key: 'Escape', keyCode: 27});
        break;
      case 'Delete':
        sendKey(this, {key: 'Delete', keyCode: 46});
        break;

      case '▲':
        sendKey(this, {key: 'ArrowUp', keyCode: 38});
        break;
      case '▼':
        sendKey(this, {key: 'ArrowDown', keyCode: 40});
        break;
      case '◀':
        sendKey(this, {key: 'ArrowLeft', keyCode: 37});
        break;
      case '▶':
        sendKey(this, {key: 'ArrowRight', keyCode: 39});
        break;

      case 'Ctrl+Alt+Delete':
        console.log('Unexpected Ctrl+Alt+Delete pressed.');
        break;
      default:
        console.log('Unexpected key pressed.');
    }
  };

  componentDidMount() {
    if (document.body.style.zoom !== undefined) {
      // the "zoom" attribute is only supported on Chromium
      document.body.ontouchend = () => {
        this.touchStartDelta = 0;
      };
      document.addEventListener('touchmove', (ev) => {
        ev.preventDefault();
        const touchEndDelta = Math.hypot(
            ev.targetTouches[0].clientX - ev.targetTouches[1].clientX,
            ev.targetTouches[0].clientY - ev.targetTouches[1].clientY);

        let newScaleLevel = this.state.scaleLevel;
        if (this.touchStartDelta !== 0) {
          if (touchEndDelta > this.touchStartDelta) {
            newScaleLevel += 0.05;
          } else {
            newScaleLevel -= 0.05;
          }
          newScaleLevel = Math.max(0.5, newScaleLevel);
          newScaleLevel = Math.min(2, newScaleLevel);
          if (this.state.scaleLevel !== newScaleLevel) {
            this.setState({
              scaleLevel: newScaleLevel,
            });
            this.term.blur();
            setTimeout(() => {
              this.term.focus();
            }, 0);
          }
        }
        this.touchStartDelta = touchEndDelta;
      }, {passive: false});
    }

    updateTitleAndIcon(this);

    termConnect(this).then();
  }

  render() {
    const {
      sessionNickname,
      authentication,
      currentStep,
      loading,
      isOverloaded,
      scaleLevel,
    } = this.state;

    return (
        <div>
          {loading &&
              <Loading
                  sessionId={this.session_id}
                  currentStep={currentStep}
                  steps={TermSteps}
                  authentication={authentication}
                  isOverloaded={isOverloaded}
              />}
          <div id="terminal" style={{
            // transform: `scale(${scaleLevel})`,
            zoom: `${scaleLevel}`,
            visibility: loading ? 'hidden' : 'visible',
            position: 'absolute',
            top: 0,
            bottom: isMobile() ? 32 * (1 / scaleLevel) : 0,
            left: 0,
            right: 0,
            background: 'black',
            zIndex: 10,
          }}/>
          {isMobile() &&
              <Toolbar onToolbarSendKey={this.handleToolbarSendKey}/>
          }
          <div style={{position: 'absolute', top: 0, left: '-100px'}}
               id={'offscreen-favicon'}>
            <BackgroundLetterAvatar
                name={sessionNickname}
                badgeContent={<div style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: COLOR_TERM_VIEWER,
                }}
                />}
            />
          </div>
        </div>
    );
  }
}