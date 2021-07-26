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

const BackgroundLetterAvatar = (props) => {
    const {name} = props;
    const hostname = name.split('.')[0];

    return (<Avatar sx={{
        backgroundColor: stringToColor(name),
        fontSize: 'small'
    }}>
        {hostname === '192' ? name.substr(-5, 5) : hostname}
    </Avatar>);
};
export default BackgroundLetterAvatar;