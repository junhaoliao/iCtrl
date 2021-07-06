export const VNCSteps = [
    {
        label: 'SSH Authentication',
        description: 'Connecting to the remote SSH machine with stored credentials (if any)...',
    },
    {
        label: '[Not Enabled] Load Check',
        description:
            'Detecting the load for the machine selected. This feature is exclusive to UofT servers. ',
    },
    {
        label: 'Parsing VNC Password',
        description:
        `Checking whether a VNC password has been configured on the remote machine. If so, we will parse that 
        and use it to protect your VNC session.`
    },
    {
        label: 'Launching VNC Session',
        description:
        `Trying to launch a VNC session on the remote machine. 
        We will try out best to reuse any pre-existing connections.`
    },
    {
        label: 'Establishing VNC Tunnel',
        description:
        `Trying to port-forward the VNC session and proxying that to a WebSocket connection, so that 
        the VNC session can be used in a browser.`
    },
    {
        label: 'Connected!',
        description:
        `Congrats!`
    }
];