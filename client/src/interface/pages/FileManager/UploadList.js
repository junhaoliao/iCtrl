import {Divider, List} from '@material-ui/core';

import UploadItem from './UploadItem';

const UploadList = (props) => {
    const {fm} = props;
    const uploadItems = fm.state.uploadProgress;
    const children = [];
    uploadItems.forEach((_, idx) => {
        children.push(
            <UploadItem key={idx} fm={fm} uploadProgressIdx={idx}/>,
        );
        if (idx !== uploadItems.length - 1) {
            children.push(<Divider key={`divider-${idx}`}/>);
        }
    });
    return (<List margin={'16px 20px 16px 20px'}>
        {children}
    </List>);
};

export default UploadList;