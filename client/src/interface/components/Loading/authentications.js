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