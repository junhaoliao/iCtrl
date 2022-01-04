import React from 'react';

import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box, Divider, Hidden
} from '@material-ui/core';
import axios from 'axios';
import ictrlLogo from '../../../icons/logo.png';
import LogIn from '../../components/LogIn';

import './index.css';

export default class Home extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        axios.get('/api/userid')
            .then(response => {
                window.location = '/dashboard';
            })
            .catch(_ => {
                // do nothing for now
            });
    }

    render() {
        return (
            <div>
                <AppBar position="static" color={'info'}>
                    <Toolbar>
                        <img src={ictrlLogo} style={{background: 'white', height: 30, width: 30, marginRight: 10}}
                             alt=""/>
                        <Typography style={{flex: 1, fontWeight: 'bold'}} variant="h6">
                            iCtrl
                        </Typography>
                        <Button color={'inherit'}>About</Button>
                    </Toolbar>
                </AppBar>

                <Box sx={{display:'flex'}}>
                    <Hidden mdDown>
                        <Box sx={{flex:5, alignSelf:'center', alignItems:'center'}}>
                            <img style={{display:'block', maxWidth: '240px', marginLeft:'auto', marginRight:'auto'}}
                            src={ictrlLogo} alt=""/>
                            <br/><br/>
                            <Typography
                                align={'center'}
                                variant={'h5'}>
                                Connect to uoft engineering labs in 5 seconds.
                            </Typography>
                        </Box>
                    </Hidden>

                    <Divider orientation="vertical" flexItem/>

                    <Box sx={{flex:3}}>
                        <LogIn/>
                    </Box>
                </Box>
                <div>
                    Intro
                </div>
            </div>
        );
    }
}


