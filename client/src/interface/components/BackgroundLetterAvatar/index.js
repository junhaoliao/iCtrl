// Reference: https://next.material-ui.com/components/avatars/
import React from 'react';
import Avatar from '@material-ui/core/Avatar';

function stringToColor(string) {
    let hash = 0;
    let i;

    for (i = 0; i < string.length; i += 1) {
        hash = string.charCodeAt(i) + ((hash << 5) - hash);
    }

    let color = '#';

    for (i = 0; i < 3; i += 1) {
        const value = (hash >> (i * 8)) & 0xff;
        color += `00${value.toString(16)}`.substr(-2);
    }

    return color;
}

function stringAvatar(name) {
    const hostname = name.split('.')[0]
    return {
        sx: {
            bgcolor: stringToColor(name),
            fontSize:'small'
        },
        children: hostname==='192'?name.substr(-5, 5):hostname,
    };
}

const BackgroundLetterAvatar = (props) => {
    return (<Avatar {...stringAvatar(props.name)} />);
};
export default BackgroundLetterAvatar;