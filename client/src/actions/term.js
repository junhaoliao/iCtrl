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

import axios from 'axios';
import {Terminal} from 'xterm';
import {WebglAddon} from 'xterm-addon-webgl';
import {AttachAddon} from 'xterm-addon-attach';
import {FitAddon} from 'xterm-addon-fit';
import {ICtrlError, ICtrlStep} from './codes';
import {
  SSHHostUnreachableRefresh,
} from '../interface/components/Loading/authentications';
import {isMobile} from './utils';

const C0 = {
  /** Null (Caret = ^@, C = \0) */
  NUL: '\x00',
  /** Start of Heading (Caret = ^A) */
  SOH: '\x01',
  /** Start of Text (Caret = ^B) */
  STX: '\x02',
  /** End of Text (Caret = ^C) */
  ETX: '\x03',
  /** End of Transmission (Caret = ^D) */
  EOT: '\x04',
  /** Enquiry (Caret = ^E) */
  ENQ: '\x05',
  /** Acknowledge (Caret = ^F) */
  ACK: '\x06',
  /** Bell (Caret = ^G, C = \a) */
  BEL: '\x07',
  /** Backspace (Caret = ^H, C = \b) */
  BS: '\x08',
  /** Character Tabulation, Horizontal Tabulation (Caret = ^I, C = \t) */
  HT: '\x09',
  /** Line Feed (Caret = ^J, C = \n) */
  LF: '\x0a',
  /** Line Tabulation, Vertical Tabulation (Caret = ^K, C = \v) */
  VT: '\x0b',
  /** Form Feed (Caret = ^L, C = \f) */
  FF: '\x0c',
  /** Carriage Return (Caret = ^M, C = \r) */
  CR: '\x0d',
  /** Shift Out (Caret = ^N) */
  SO: '\x0e',
  /** Shift In (Caret = ^O) */
  SI: '\x0f',
  /** Data Link Escape (Caret = ^P) */
  DLE: '\x10',
  /** Device Control One (XON) (Caret = ^Q) */
  DC1: '\x11',
  /** Device Control Two (Caret = ^R) */
  DC2: '\x12',
  /** Device Control Three (XOFF) (Caret = ^S) */
  DC3: '\x13',
  /** Device Control Four (Caret = ^T) */
  DC4: '\x14',
  /** Negative Acknowledge (Caret = ^U) */
  NAK: '\x15',
  /** Synchronous Idle (Caret = ^V) */
  SYN: '\x16',
  /** End of Transmission Block (Caret = ^W) */
  ETB: '\x17',
  /** Cancel (Caret = ^X) */
  CAN: '\x18',
  /** End of Medium (Caret = ^Y) */
  EM: '\x19',
  /** Substitute (Caret = ^Z) */
  SUB: '\x1a',
  /** Escape (Caret = ^[, C = \e) */
  ESC: '\x1b',
  /** File Separator (Caret = ^\) */
  FS: '\x1c',
  /** Group Separator (Caret = ^]) */
  GS: '\x1d',
  /** Record Separator (Caret = ^^) */
  RS: '\x1e',
  /** Unit Separator (Caret = ^_) */
  US: '\x1f',
  /** Space */
  SP: '\x20',
  /** Delete (Caret = ^?) */
  DEL: '\x7f',
};

// reg + shift key mappings for digits and special chars
const KEYCODE_KEY_MAPPINGS = {
  // digits 0-9
  48: ['0', ')'],
  49: ['1', '!'],
  50: ['2', '@'],
  51: ['3', '#'],
  52: ['4', '$'],
  53: ['5', '%'],
  54: ['6', '^'],
  55: ['7', '&'],
  56: ['8', '*'],
  57: ['9', '('],

  // special chars
  186: [';', ':'],
  187: ['=', '+'],
  188: [',', '<'],
  189: ['-', '_'],
  190: ['.', '>'],
  191: ['/', '?'],
  192: ['`', '~'],
  219: ['[', '{'],
  220: ['\\', '|'],
  221: [']', '}'],
  222: ['\'', '"'],
};

const KEY_KEYCODE_MAPPINGS = {
  ' ': 32,

  '3': 51,
  '4': 52,
  '5': 53,
  '6': 54,
  '7': 55,
  '8': 56,

  '#': 51,
  '$': 52,
  '%': 53,
  '^': 54,
  '&': 55,
  '*': 56,

  '[': 219,
  '\\': 220,
  ']': 221,

  '{': 219,
  '|': 220,
  '}': 221,

};

// TODO: support the other keys
const evaluateKeyboardEvent = (
    ev,
    applicationCursorMode,
    isMac,
    macOptionIsMeta,
) => {
  const result = {
    type: 0, // KeyboardResultType.SEND_KEY,
    // Whether to cancel event propagation (NOTE: this may not be needed since the event is
    // canceled at the end of keyDown
    cancel: false,
    // The new key even to emit
    key: undefined,
  };
  const modifiers = (ev.shiftKey ? 1 : 0) | (ev.altKey ? 2 : 0) |
      (ev.ctrlKey ? 4 : 0) | (ev.metaKey ? 8 : 0);
  switch (ev.keyCode) {
    case 0:
      if (ev.key === 'UIKeyInputUpArrow') {
        if (applicationCursorMode) {
          result.key = C0.ESC + 'OA';
        } else {
          result.key = C0.ESC + '[A';
        }
      } else if (ev.key === 'UIKeyInputLeftArrow') {
        if (applicationCursorMode) {
          result.key = C0.ESC + 'OD';
        } else {
          result.key = C0.ESC + '[D';
        }
      } else if (ev.key === 'UIKeyInputRightArrow') {
        if (applicationCursorMode) {
          result.key = C0.ESC + 'OC';
        } else {
          result.key = C0.ESC + '[C';
        }
      } else if (ev.key === 'UIKeyInputDownArrow') {
        if (applicationCursorMode) {
          result.key = C0.ESC + 'OB';
        } else {
          result.key = C0.ESC + '[B';
        }
      }
      break;
    case 8:
      // backspace
      if (ev.shiftKey) {
        result.key = C0.BS; // ^H
        break;
      } else if (ev.altKey) {
        result.key = C0.ESC + C0.DEL; // \e ^?
        break;
      }
      result.key = C0.DEL; // ^?
      break;
    case 9:
      // tab
      if (ev.shiftKey) {
        result.key = C0.ESC + '[Z';
        break;
      }
      result.key = C0.HT;
      result.cancel = true;
      break;
    case 13:
      // return/enter
      result.key = ev.altKey ? C0.ESC + C0.CR : C0.CR;
      result.cancel = true;
      break;
    case 27:
      // escape
      result.key = C0.ESC;
      if (ev.altKey) {
        result.key = C0.ESC + C0.ESC;
      }
      result.cancel = true;
      break;
    case 37:
      // left-arrow
      if (ev.metaKey) {
        break;
      }
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'D';
        // HACK: Make Alt + left-arrow behave like Ctrl + left-arrow: move one word backwards
        // http://unix.stackexchange.com/a/108106
        // macOS uses different escape sequences than linux
        if (result.key === C0.ESC + '[1;3D') {
          result.key = C0.ESC + (isMac ? 'b' : '[1;5D');
        }
      } else if (applicationCursorMode) {
        result.key = C0.ESC + 'OD';
      } else {
        result.key = C0.ESC + '[D';
      }
      break;
    case 39:
      // right-arrow
      if (ev.metaKey) {
        break;
      }
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'C';
        // HACK: Make Alt + right-arrow behave like Ctrl + right-arrow: move one word forward
        // http://unix.stackexchange.com/a/108106
        // macOS uses different escape sequences than linux
        if (result.key === C0.ESC + '[1;3C') {
          result.key = C0.ESC + (isMac ? 'f' : '[1;5C');
        }
      } else if (applicationCursorMode) {
        result.key = C0.ESC + 'OC';
      } else {
        result.key = C0.ESC + '[C';
      }
      break;
    case 38:
      // up-arrow
      if (ev.metaKey) {
        break;
      }
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'A';
        // HACK: Make Alt + up-arrow behave like Ctrl + up-arrow
        // http://unix.stackexchange.com/a/108106
        // macOS uses different escape sequences than linux
        if (!isMac && result.key === C0.ESC + '[1;3A') {
          result.key = C0.ESC + '[1;5A';
        }
      } else if (applicationCursorMode) {
        result.key = C0.ESC + 'OA';
      } else {
        result.key = C0.ESC + '[A';
      }
      break;
    case 40:
      // down-arrow
      if (ev.metaKey) {
        break;
      }
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'B';
        // HACK: Make Alt + down-arrow behave like Ctrl + down-arrow
        // http://unix.stackexchange.com/a/108106
        // macOS uses different escape sequences than linux
        if (!isMac && result.key === C0.ESC + '[1;3B') {
          result.key = C0.ESC + '[1;5B';
        }
      } else if (applicationCursorMode) {
        result.key = C0.ESC + 'OB';
      } else {
        result.key = C0.ESC + '[B';
      }
      break;
    case 45:
      // insert
      if (!ev.shiftKey && !ev.ctrlKey) {
        // <Ctrl> or <Shift> + <Insert> are used to
        // copy-paste on some systems.
        result.key = C0.ESC + '[2~';
      }
      break;
    case 46:
      // delete
      if (modifiers) {
        result.key = C0.ESC + '[3;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[3~';
      }
      break;
    case 36:
      // home
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'H';
      } else if (applicationCursorMode) {
        result.key = C0.ESC + 'OH';
      } else {
        result.key = C0.ESC + '[H';
      }
      break;
    case 35:
      // end
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'F';
      } else if (applicationCursorMode) {
        result.key = C0.ESC + 'OF';
      } else {
        result.key = C0.ESC + '[F';
      }
      break;
    case 33:
      // page up
      if (ev.shiftKey) {
        result.type = 2; // KeyboardResultType.PAGE_UP;
      } else {
        result.key = C0.ESC + '[5~';
      }
      break;
    case 34:
      // page down
      if (ev.shiftKey) {
        result.type = 3; // KeyboardResultType.PAGE_DOWN;
      } else {
        result.key = C0.ESC + '[6~';
      }
      break;
    case 112:
      // F1-F12
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'P';
      } else {
        result.key = C0.ESC + 'OP';
      }
      break;
    case 113:
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'Q';
      } else {
        result.key = C0.ESC + 'OQ';
      }
      break;
    case 114:
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'R';
      } else {
        result.key = C0.ESC + 'OR';
      }
      break;
    case 115:
      if (modifiers) {
        result.key = C0.ESC + '[1;' + (modifiers + 1) + 'S';
      } else {
        result.key = C0.ESC + 'OS';
      }
      break;
    case 116:
      if (modifiers) {
        result.key = C0.ESC + '[15;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[15~';
      }
      break;
    case 117:
      if (modifiers) {
        result.key = C0.ESC + '[17;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[17~';
      }
      break;
    case 118:
      if (modifiers) {
        result.key = C0.ESC + '[18;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[18~';
      }
      break;
    case 119:
      if (modifiers) {
        result.key = C0.ESC + '[19;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[19~';
      }
      break;
    case 120:
      if (modifiers) {
        result.key = C0.ESC + '[20;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[20~';
      }
      break;
    case 121:
      if (modifiers) {
        result.key = C0.ESC + '[21;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[21~';
      }
      break;
    case 122:
      if (modifiers) {
        result.key = C0.ESC + '[23;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[23~';
      }
      break;
    case 123:
      if (modifiers) {
        result.key = C0.ESC + '[24;' + (modifiers + 1) + '~';
      } else {
        result.key = C0.ESC + '[24~';
      }
      break;
    default:
      // a-z and space
      if (ev.ctrlKey && !ev.shiftKey && !ev.altKey && !ev.metaKey) {
        if (ev.keyCode >= 65 && ev.keyCode <= 90) {
          result.key = String.fromCharCode(ev.keyCode - 64);
        } else if (ev.keyCode === 32) {
          result.key = C0.NUL;
        } else if (ev.keyCode >= 51 && ev.keyCode <= 55) {
          // escape, file sep, group sep, record sep, unit sep
          result.key = String.fromCharCode(ev.keyCode - 51 + 27);
        } else if (ev.keyCode === 56) {
          result.key = C0.DEL;
        } else if (ev.keyCode === 219) {
          result.key = C0.ESC;
        } else if (ev.keyCode === 220) {
          result.key = C0.FS;
        } else if (ev.keyCode === 221) {
          result.key = C0.GS;
        }
      } else if ((!isMac || macOptionIsMeta) && ev.altKey && !ev.metaKey) {
        // On macOS this is a third level shift when !macOptionIsMeta. Use <Esc> instead.
        const keyMapping = KEYCODE_KEY_MAPPINGS[ev.keyCode];
        const key = keyMapping && keyMapping[!ev.shiftKey ? 0 : 1];
        if (key) {
          result.key = C0.ESC + key;
        } else if (ev.keyCode >= 65 && ev.keyCode <= 90) {
          const keyCode = ev.ctrlKey ? ev.keyCode - 64 : ev.keyCode + 32;
          result.key = C0.ESC + String.fromCharCode(keyCode);
        }
      } else if (isMac && !ev.altKey && !ev.ctrlKey && !ev.shiftKey &&
          ev.metaKey) {
        if (ev.keyCode === 65) { // cmd + a
          result.type = 1; // KeyboardResultType.SELECT_ALL;
        }
      } else if (ev.key === ' ' ||
          (ev.key && !ev.ctrlKey && !ev.altKey && !ev.metaKey && ev.keyCode >=
              48 && ev.key.length === 1)) {
        // Include only keys that that result in a _single_ character; don't include num lock, volume up, etc.
        result.key = ev.key;
      } else if (ev.key && ev.ctrlKey) {
        if (ev.key === '_') { // ^_
          result.key = C0.US;
        }
      }
      break;
  }
  return result;
};

export const sendKey = (TermViewer, ev) => {
  const options = {
    ctrlKey: ev.ctrlKey || TermViewer.ctrlKey,
    shiftKey: ev.shiftKey || TermViewer.shiftKey,
    metaKey: ev.metaKey || TermViewer.metaKey,
    altKey: ev.altKey || TermViewer.altKey,
    key: ev.key,
    keyCode: ev.keyCode,
  };
  if (ev.keyCode === 229) {
    const oldValue = TermViewer.term.textarea.value;
    TermViewer.term.textarea.setSelectionRange(oldValue.length,
        oldValue.length);
    setTimeout(() => {
      const newValue = TermViewer.term.textarea.value;
      if (newValue === '_') {
        sendKey(TermViewer, {key: 'Backspace', keyCode: 8});
      } else {
        const diff = newValue.replace(oldValue, '');

        if (diff.length === 1) {
          const charCode = diff.charCodeAt(0);
          // try our best to match the char with the keycodes
          //  so that the ctrl/alt/shift combinations will work
          if (charCode >= 65 && charCode <= 90) {
            sendKey(TermViewer, {...options, key: diff, keyCode: charCode});
          } else if (charCode >= 97 && charCode <= 122) {
            sendKey(TermViewer, {
              ...options,
              key: options.shiftKey ? diff.toUpperCase() : diff,
              keyCode: charCode - 0x20,
            });
          } else if (diff in KEY_KEYCODE_MAPPINGS) {
            sendKey(TermViewer,
                {...options, key: diff, keyCode: KEY_KEYCODE_MAPPINGS[diff]});
          } else {
            TermViewer.term._core.coreService.triggerDataEvent(diff, true);
          }
        } else {
          TermViewer.term._core.coreService.triggerDataEvent(diff, true);
        }
      }

      TermViewer.term.textarea.value = '__';
      TermViewer.term.textarea.setSelectionRange(1, 1);
    }, 0);
    return false;
  } else if (ev.key === 'ArrowLeft') {
    TermViewer.term.textarea.setSelectionRange(2, 2);
  } else if (ev.key === 'ArrowRight') {
    TermViewer.term.textarea.setSelectionRange(0, 0);
  }

  const result = evaluateKeyboardEvent(
      options,
      TermViewer.term._core.coreService.decPrivateModes.applicationCursorKeys,
      TermViewer.term._core.browser.isMac,
      TermViewer.term._core.options.macOptionIsMeta,
  );
  if (!result.key) {
    return true;
  }

  // if ev is a real event, ev.target will be defined
  // if not then ev is not a KeyEvent: take a look at the call stack
  if (result.cancel && ev.target) {
    TermViewer.term._core.cancel(ev, true);
  }
  TermViewer.term._core.coreService.triggerDataEvent(result.key, true);

  return false;
};

const setupDOM = (TermViewer) => {
  const term_div = document.getElementById('terminal');

  TermViewer.term = new Terminal();
  TermViewer.term.open(term_div);

  // setup beeping sound
  // credits: Gnome: /usr/share/sounds/gnome/default/alerts/drip.ogg
  TermViewer.term.setOption('bellStyle', 'sound');
  TermViewer.term.setOption('bellSound',
      'data:audio/ogg;base64,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MsYYY85BCJ1zjjHnIITQOceYcxBC55xjzDkIoXOMMeacAACgAgcAgAAbRTYnGAkqNGQlABAOAAAYw5hzjDkGnYQKIecgdA5CKqlUCDkHoXMQSkmpeA46KSGUUkoqxXMQSgmhlJRaKy6GUkoopaTUUpExhFJKKSWl1ooxpoSQUkqptVaMMaGEVFJKKbZijI2lpNRaa60VY2wsJZXWWmutGGOMaym1FmOsxRhjXEuppRhrLMYY43tqLcZYYzHGGJ9baimmXAsAMHlwAIBKsHGGlaSzwtHgQkNWAgC5AQAIQkoxxphjzjnnnHPOSaUYc8455yCEEEIIIZRKMeacc85BByGEEEIoGXPOOQchhBBCCCGEUFLqmHMOQgghhBBCCCGl1DnnIIQQQgghhBBCSqlzzkEIIYQQQgghhJRSCCGEEEIIIYQQQggppZRCCCGEEEIIIZQSUkophRBCCCWEEkoIJaSUUgohhBBCKaWEUkJJKaUUQgillFBKKaGUkFJKKaUQQiillFBKKSWllFJKJZRSSikllFBKSimllEoooZRQSimllJRSSimVUkopJZRSSgkppZRSSqmUUkoppZRSUkoppZRSKaWUUkoppaSUUkoppVJKKaWUEkpJKaWUUkqllFBKKaWUUlJKKaWUSgqllFJKKaUAAKADBwCAACMqLcROM648AkcUMkxAhYasBABSAQAAQiillFJKKTWMUUoppZRSihyklFJKKaWUUkoppZRSSimVUkoppZRSSimllFJKKaWUUkoppZRSSimllFJKKaWUUkoppZRSSimllFJKKaWUUkoppZRSSimllFJKKaWUUkoppZRSSimllFJKAcDdFw6APhM2rI5wUjQWWGjISgAgFQAAMIYxxphyzjmllHPOOQadlEgp5yB0TkopPYQQQgidhJR6ByGEEEIpKfUYQyghlJRS67GGTjoIpbTUaw8hhJRaaqn3HjKoKKWSUu89tVBSainG3ntLJbPSWmu9595LKinG2nrvObeSUkwtFgBgEuEAgLhgw+oIJ0VjgYWGrAIAYgAACEMMQkgppZRSSinGGGOMMcYYY4wxxhhjjDHGGGOMMQEAgAkOAAABVrArs7Rqo7ipk7zog8AndMRmZMilVMzkRNAjNdRiJdihFdzgBWChISsBADIAAMRRrDXGXitiGISSaiwNQYxBibllxijlJObWKaWU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');

  TermViewer.term.setOption('rightClickSelectsWord', false);

  if (isMobile()) {
    // give some text so that both 'ArrowLeft' and 'ArrowRight' can be triggered
    TermViewer.term.textarea.value = '__';
    TermViewer.term.textarea.setSelectionRange(1, 1);

    TermViewer.term.attachCustomKeyEventHandler((ev) => {
      if (ev.type !== 'keydown') {
        return false;
      }
      return sendKey(TermViewer, ev);
    });
  }

  return term_div;
};

const setupWebGL = (term) => {
  const addon = new WebglAddon();
  addon.onContextLoss(_ => {
    addon.dispose();
  });
  term.loadAddon(addon);
};

const setupWebSocket = (term, term_id, port) => {

  const socket = new WebSocket(
      `${process.env.REACT_APP_DOMAIN_NAME ? 'wss' : 'ws'}
://${process.env.REACT_APP_DOMAIN_NAME || '127.0.0.1'}:${port}/${term_id}`);

  socket.onopen = (_) => {
    const attachAddon = new AttachAddon(socket);
    term.loadAddon(attachAddon);
  };
  socket.onclose = (ev) => {
    term.write(
        '\r\niCtrl: WebSocket closed. \r\nYou may press Ctrl + R to reload. ');
    term.onData(chunk => {
      if (chunk === '') {
        window.location.reload();
      }
    });
  };

  return socket;
};

const setupCopyPaste = (term, term_div, socket) => {
  try {
    navigator.clipboard.readText().then(_ => {
      term_div.onauxclick = (ev) => {
        if (ev.button === 2) {
          const selection = term.getSelection();
          if (selection === '') {
            navigator.clipboard.readText().then(text => {
              socket.send(text);
            });
          } else {
            navigator.clipboard.writeText(selection).then();
            term.clearSelection();
          }
        }
      };
      term_div.oncontextmenu = (ev) => {
        // prevent the context menu from opening
        ev.preventDefault();
      };
    }).catch(error => {
      // clipboard permission not given
      console.log(error);
    });
  } catch (e) {
    console.log('clipboard not permitted / supported');
  }
};

const setupResize = (term, sessionID, term_id) => {
  let resize_timeout = null;
  term.onResize(({cols, rows}) => {
    // add a 500 ms delay to prevent requesting terminal resize too frequently,
    //  thus saving network bandwidth among the client, the server, and the target
    clearTimeout(resize_timeout);
    resize_timeout = setTimeout(() => {
      axios.patch(`/api/terminal_resize`, {
        session_id: sessionID,
        term_id: term_id,
        w: cols,
        h: rows,
      }).then(_ => {
        term.scrollToBottom();
      }).catch(error => {
        console.log(error);
      });
    }, 500);
  });
  const fitAddon = new FitAddon();
  term.loadAddon(fitAddon);
  fitAddon.fit();
  window.onresize = () => {
    fitAddon.fit();
  };
};

export const termConnect = async (TermViewer) => {
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: TermViewer.session_id,
      no_load_check: TermViewer.noLoadCheck,
    }),
  };

  const response = await fetch(`/api/terminal`, options);
  if (response.status !== 200) {
    console.log(response.body);
    return;
  }

  const reader = response.body.getReader();
  // this will store all the data read from the stream
  const data = [];
  const readStream = ({value, done}) => {
    // if the stream reading is done (end of stream),
    //  ignore all the step codes and parse the final response as JSON
    if (done) {
      const resultArr = new Uint8Array(
          data.slice(data.indexOf(ICtrlStep.Term.DONE) + 1));
      const decodedStr = new TextDecoder().decode(resultArr);
      const {term_id, port} = JSON.parse(decodedStr);

      const term_div = setupDOM(TermViewer);

      if (!isMobile()) {
        // setting WebGL should improve rendering speed
        //  but it seems it is not well supported on most mobile browser
        setupWebGL(TermViewer.term);
      }

      const socket = setupWebSocket(TermViewer.term, term_id, port);
      setupCopyPaste(TermViewer.term, term_div, socket);
      setupResize(TermViewer.term, TermViewer.session_id, term_id);

      /* need to set the state 'loading' to false so that the term div is visible and can be focused on */
      TermViewer.setState({
        loading: false,
      });

      /* focus on the terminal once everything finishes loading */
      TermViewer.term.focus();

      return;
    } // if (done)

    // if the stream is not finished, push the values that was read into 'data'
    data.push(...value);

    // the stream is in this format:
    // STEP1 | STEP2 | ... | _DONE_ | FINAL_RESPONSE
    // from above we can see step 'DONE' serve as a divider of the step codes and the final response

    // if the step 'DONE' is present in 'data'
    if (data.includes(ICtrlStep.Term.DONE)) {
      // update the current step to 'DONE' and wait for the whole stream to be transferred
      TermViewer.setState({
        currentStep: ICtrlStep.Term.DONE,
      });
    } else {
      // if the step 'DONE' is not present in 'data',
      //  the last digit in the array must still be a step code
      //  rather than part of the final response
      const currentStep = value.slice(-1)[0];
      if (currentStep < 100) {
        // not an error
        TermViewer.setState({
          currentStep: currentStep,
        });
      } else {
        TermViewer.setState({
          currentStep: data.slice(-2)[0],
        });
        // handle the errors / server requests
        if (currentStep === ICtrlError.SSH.HOST_UNREACHABLE) {
          TermViewer.setState({
            authentication: SSHHostUnreachableRefresh,
          });
        } else if (currentStep === ICtrlError.SSH.OVER_LOADED) {
          TermViewer.setState({
            isOverloaded: true,
          });
        } else {
          console.log(`Term error code: ${currentStep}`);
          console.log(data);
        }

        // stop reading the stream now that an error occurs
        return;
      }

    }

    reader.read().then(readStream);
  };
  // make the call to read the stream
  reader.read().then(readStream);
};