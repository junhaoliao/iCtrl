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

export const SSHNoKeyAuthentication = {
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