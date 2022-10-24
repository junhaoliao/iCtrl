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

export const VNCSteps = [
  {
    label: 'SSH Authentication',
    description: 'Connecting to the remote SSH machine...',
  },
  {
    label: 'Load Check',
    description:
        'Detecting the load for the machine selected. This feature is exclusive to UofT servers. ',
  },
  {
    label: 'Parsing VNC Password',
    description:
        `Checking whether a VNC password has been configured on the remote machine. If so, we will parse that 
        and use it to protect your VNC session.`,
  },
  {
    label: 'Launching VNC Session',
    description:
        `Trying to launch a VNC session on the remote machine. 
        We will try our best to reuse any pre-existing connections.`,
  },
  {
    label: 'Establishing VNC Tunnel',
    description:
        `Trying to port-forward the VNC session and proxying that to a WebSocket connection, so that 
        the VNC session can be used in a browser.`,
  },
  {
    label: 'Connected!',
    description:
        `Congrats!`,
  },
];

export const TermSteps = [
  {
    label: 'SSH Authentication',
    description: 'Connecting to the remote SSH machine...',
  },
  {
    label: 'Load Check',
    description:
        'Detecting the load for the machine selected. This feature is exclusive to UofT servers. ',
  },
  {
    label: 'Launching Shell',
    description:
        'Invoking a shell and setting up the I/O forwarding. ',
  },
  {
    label: 'Connected!',
    description:
        `Congrats!`,
  },
];