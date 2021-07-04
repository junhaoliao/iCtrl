import {Box, Divider} from '@material-ui/core';

import UploadItem from './UploadItem';

const UploadList = (props) => {
    const {fm} = props;
    const uploadItems = fm.state.uploadProgress;
    const children = uploadItems.map((_, idx) => (
        <div key={idx}>
            <UploadItem fm={fm} uploadProgressIdx={idx}/>
            {(idx !== uploadItems.length - 1) && <Divider/>}
        </div>
    ));
    return (<Box margin={'16px 20px 16px 20px'} display={'vertical'}>
        {children}
    </Box>);
};

export default UploadList;