/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import { Dialog, DialogActions, Typography } from '@material-ui/core';
import axios from 'axios';

import './index.css';

export default class NewSession extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            open: true,
        }
    }

    handleClickOpen() {
        this.setState({ open: true });
      };
    
    handleClose() {
        this.props.handleDone()
        this.setState({ open: false });
    };

    handleSave() {
        // to do
        const host = document.getElementById('host').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        // console.log(hostname, username, password)
        axios.post('/session', {
            host, username, password
        }).then(response => {
            console.log(response.data);
        }).catch(err => {
            console.log('error', err)
        })
        this.handleClose();
    }

    render() {
        const { open } = this.state;
        return (
            <Dialog
                open={open}
                onClose={() => this.handleClose()}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
            >
                <div className="new-session-content-wrapper">
                    <div className="new-session-input-wrapper">
                        <div className="new-session-name-wrapper">
                        <Typography class="new-session-name" variant={'h6'}>
                            HostName*
                        </Typography>
                        <Typography class="new-session-name" variant={'h6'}>
                            UserName*
                        </Typography>
                        <Typography class="new-session-name" variant={'h6'}>
                            Password
                        </Typography>
                        </div>
                        <div className="new-session-inputs">
                            <TextField id="host" label="Required" variant="outlined" />
                            <TextField id="username" label="Required" variant="outlined" />
                            <TextField id="password" label="Optional" variant="outlined" />
                        </div>
                        
                    </div>
                    <DialogActions>
                        <Button onClick={() => this.handleClose()}>Close</Button>
                        <Button variant={'contained'} id={'button_cancel'} onClick={() => this.handleSave()}>Save</Button>
                    </DialogActions>
                    {/* <div className="new-session-save">
                        <Button variant="contained" color="secondary" onClick={() => this.handleClose()}>Close</Button>
                        <Button style={{ marginLeft: 20 }} variant="contained" color="primary" onClick={() => this.handleSave()}>Save</Button>
                    </div> */}
                </div>
            </Dialog>
        )
    }
}