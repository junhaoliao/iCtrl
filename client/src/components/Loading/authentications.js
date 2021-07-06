export const SSHNoKeyAuthentication = {
    label: 'Please enter your SSH password',
    description: `We can't find any SSH keys for the connection. 
    Please enter your password for the SSH connection`,
    validator: (_) => {
        return ' ';
    },
    submitter: (authInput) => {
        console.log('Virtual submitter not overridden: ', authInput);
    }
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
    submitter: (authInput) => {
        console.log(authInput);
    }
};