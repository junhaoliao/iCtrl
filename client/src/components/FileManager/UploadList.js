import UploadItem from './UploadItem';
import {Box} from '@material-ui/core';


const UploadList = (props) => {
    console.log('render');
    const {items} = props;
    const children = items.map((i) => (
        <UploadItem
            filename={i['name']}
            progress={i['progress']}
        />
    ));
    return (<Box margin={'16px 20px 16px 20px'} display={'vertical'}>
        {children}
    </Box>);
};

export default UploadList;