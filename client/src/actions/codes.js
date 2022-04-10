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

export const STEP_DONE = 31;
const ERROR_GENERAL = 100;

class VNCError {
  static GENERAL = ERROR_GENERAL + 20;
  static PASSWD_MISSING = this.GENERAL + 1;
  static QUOTA_EXCEEDED = this.GENERAL + 2;
}

class SSHError {
  static GENERAL = 200;
  static HOST_UNREACHABLE = this.GENERAL + 1;
  static AUTH_MISSING = this.GENERAL + 2;
  static AUTH_WRONG = this.GENERAL + 3;
  static OVER_LOADED = this.GENERAL + 4;
}

export const ICtrlError = {
  VNC: VNCError,
  SSH: SSHError,
};

const VNCStepCodes = {
  SSH_AUTH: 0,
  CHECK_LOAD: 1,
  PARSE_PASSWD: 2,
  LAUNCH_VNC: 3,
  CREATE_TUNNEL: 4,
  DONE: STEP_DONE,
};

const TermStepCodes = {
  SSH_AUTH: 0,
  CHECK_LOAD: 1,
  LAUNCH_SHELL: 2,
  DONE: STEP_DONE,
};

export const ICtrlStep = {
  VNC: VNCStepCodes,
  Term: TermStepCodes,
};