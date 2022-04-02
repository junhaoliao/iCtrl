import React from 'react';
import {sftp_quota} from '../../../actions/sftp';
import {Box, LinearProgress, Skeleton, Typography} from '@material-ui/core';

function LinearProgressWithLabel(props) {
    return (
        <Box sx={{display: 'flex', alignItems: 'center'}}>
            <Box flexGrow={1}>
                <LinearProgress
                    variant={props.loading ? 'indeterminate' : 'determinate'}
                    value={props.value}
                />
            </Box>
            <Box sx={{marginLeft: 1.5}}>
                <Typography display={'flex'} variant="body2" color="text.secondary">
                    {props.loading ? <Skeleton width={15}/> : `${Math.round(props.value)}`}%
                </Typography>
            </Box>
        </Box>
    );
}


export default class QuotaUsage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            used: 0,
            usedUnit: '',
            quota: 0,
            quotaUnit: '',
        };
    }

    componentDidMount() {
        const {sessionID} = this.props;
        sftp_quota(
            sessionID,
            this,
        );
    }

    render() {
        const {
            used,
            usedUnit,
            quota,
            quotaUnit,
        } = this.state;
        const loading = (quota === 0);
        const loadFailed = (quota === null);
        return (<div style={{width: '100%', visibility: loadFailed ? 'hidden' : 'visible'}}>
                <LinearProgressWithLabel loading={loading}
                                         value={used / quota * 100}/>
                <Typography variant="caption" display={'flex'}>
                    {loading ? <Skeleton width={44}/> : `${used}${usedUnit}`}
                    {' / '}
                    {loading ? <Skeleton width={44}/> : `${quota}${quotaUnit}`}
                    {' Used'}
                </Typography>
            </div>
        );
    }
}