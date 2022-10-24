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

export const SSHHostUnreachableRefresh = {
  label: 'Host Unreachable',
  description: `We are unable to reach the SSH host. 
    Please contact the host administrator or refresh this page to reconnect.`,
  validator: null,
  submitterName: 'Refresh',
  submitter: () => {
    window.location.reload();
  },
};

// TODO: implement this in the future
export const SSHAuthenticationMissing = {
  label: 'Please enter your SSH password',
  description: `We can't find any SSH keys for the connection. 
    Please enter your password for the SSH connection:`,
  validator: (_) => {
    return ' ';
  },
  submitterName: 'Confirm',
  submitter: (authInput) => {
    console.log('Virtual submitter not overridden: ', authInput);
  },
};

// FIXME: this is a temporary solution to mismatching keys
//  Eventually, SSHNoKeyAuthentication can be used instead if it is implemented
export const SSHAuthenticationWrong = {
  label: 'Unable to match key pairs',
  description: `iCtrl is unable to match any keys on the remote host. 
  This may mean the remote host was re-imaged or the hostname is now being 
  resolved to a different machine.   If you are certain those keys are no 
  longer recoverable, please close this window and go to the iCtrl Dashboard to 
  remove this session. Then you may recreate one with the same host name. `,
  validator: null,
  submitterName: 'Close',
  submitter: () => {
    window.close()
  },
};

export const VNCAuthentication = {
  label: 'Please set a VNC password',
  description: `The password should contain only ASCII characters 
    (numbers, letters and symbols that you can find on a US keyboard).`,
  validator: (newAuthInput) => {
    if (newAuthInput.length < 6) {
      return 'The minimum length is 6 characters.';
    }
    return ' ';
  },
  submitterName: 'Confirm',
  submitter: (authInput) => {
    console.log(authInput);
  },
};