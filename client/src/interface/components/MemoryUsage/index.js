import React from 'react';
import { sftp_quota } from '../../../actions/sftp';
import {
    Box,
    LinearProgress,
    Typography
} from '@material-ui/core'

function LinearProgressWithLabel(props) {
    return (
        <Box sx={{display: 'flex', alignItems: 'center'}}>
            <Box sx={{width: '100%', mr: 1}}>
                <LinearProgress variant="determinate" {...props} />
            </Box>
            <Box sx={{minWidth: 35}}>
                <Typography variant="body2" color="text.secondary">{`${Math.round(
                    props.value,
                )}%`}</Typography>
            </Box>
        </Box>
    );
}


export default class MemoryUsage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            memQuota:  0,
            memUnit: '',
            memUsed: 0
        }
    }

    componentDidMount() {
        sftp_quota(
            this.props.fm,
            this.props.fm.state.cwd,
            this
        )
    }

    render() {
        return (<div>
            <LinearProgressWithLabel variant="determinate" value={this.state.memUsed / this.state.memQuota * 100}/>
            <Typography variant="caption" display="block">
                {this.state.memUsed} {this.state.memUnit} of {this.state.memQuota} {this.state.memUnit} Used
            </Typography>
            </div>
        );
    }
}