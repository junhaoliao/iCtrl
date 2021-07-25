import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import {Box, Dialog, DialogActions, DialogTitle, Tooltip, Typography} from '@material-ui/core';
import axios from 'axios';

import './index.css';

export default class NewSession extends React.Component {
    handleSubmit() {
        const host = document.getElementById('host').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        axios.post('/session', {
            host, username, password
        }).then(response => {
            console.log(response.data);
            window.location.reload();
        }).catch(err => {
            console.log('error', err);
        });
    }

    handleClose = (ev) => {
        if (ev.target && ev.target.id === 'button-save') {
            this.handleSubmit();
        }
        this.props.onAddNewSessionClose();
    };

    shiftFocus = (ev) => {
        // only shift the focus if the 'Enter'/'Return' key is pressed
        if (ev.key !== 'Enter'){
            return
        }

        const id = ev.target.id

        // all fields are required except 'password'
        if (id==='password' && ev.target.value.length === 0){
            return;
        }

        let nextField = null

        if (id === 'host'){
            nextField = document.getElementById('username')
        } else if (id === 'username'){
            nextField = document.getElementById('password')
        } else if (id === 'password'){
            nextField = document.getElementById('button-save')
        } else {
            // should never reach here,
            //  or this callback is used in a wrong place
            throw Error('wrong branch')
        }

        nextField.focus()
    };

    render() {
        const {open} = this.props;
        return (
            <Dialog
                open={open}
                fullWidth={true}
                maxWidth={'xs'}
                aria-labelledby="new session"
            >
                <DialogTitle>Create New Session</DialogTitle>

                <div className={'new-session-content-wrapper'}>
                    <Box display={'flex'}>
                        <Tooltip flexGrow={1} title={'[Required] host name of the target SSH server'}>
                            <Typography variant={'subtitle1'}>Host<span style={{color: 'red'}}>*</span></Typography>
                        </Tooltip>
                        <TextField id={'host'}
                                   autoFocus
                                   autoComplete={'off'}
                                   style={{width: 250}}
                                   size={'small'}
                                   placeholder={'example.com'}
                                   variant={'standard'}
                                   onKeyDown={this.shiftFocus}
                        />
                    </Box>
                    <Box display={'flex'}>
                        <Tooltip flexGrow={1} title={'[Required] username for login'}>
                            <Typography variant={'subtitle1'}>Username<span style={{color: 'red'}}>*</span></Typography>
                        </Tooltip>
                        <TextField id={'username'}
                                   autoComplete={'off'}
                                   style={{width: 250}}
                                   size={'small'}
                                   placeholder={'username'}
                                   variant={'standard'}
                                   onKeyDown={this.shiftFocus}
                        />
                    </Box>
                    <Box display={'flex'}>
                        <Tooltip flexGrow={1} title={'[Optional] password for login'}>
                            <Typography variant={'subtitle1'}>Password</Typography>
                        </Tooltip>
                        <TextField id={'password'}
                                   type={'password'}
                                   autoComplete={'off'}
                                   style={{width: 250}}
                                   size={'small'}
                                   placeholder={'****'}
                                   variant={'standard'}
                                   onKeyDown={this.shiftFocus}
                        />
                    </Box>

                </div>
                <DialogActions>
                    <Button onClick={this.handleClose}>Close</Button>
                    <Button variant={'contained'}
                            id={'button-save'}
                            onClick={this.handleClose}>
                        Save
                    </Button>
                </DialogActions>

            </Dialog>
        );
    }
}