/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';

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
        this.handleClose();
    }

    render() {
        const { open } = this.state;
        return (
            <div className="new-session-bg">
                <div className="new-session-mask" />
                <div>
                    <Dialog
                        open={open}
                        onClose={() => this.handleClose()}
                        aria-labelledby="alert-dialog-title"
                        aria-describedby="alert-dialog-description"
                    >
                        <div className="new-session-content-wrapper">
                            <div className="new-session-input-wrapper">
                                <div className="new-session-name-wrapper">
                                    <div className="new-session-name">HostName*</div>
                                    <div className="new-session-name">UserName*</div>
                                    <div className="new-session-name">Password</div>
                                </div>
                                <div className="new-session-inputs">
                                    <TextField id="outlined-basic" label="Required" variant="outlined" />
                                    <TextField id="outlined-basic" label="Required" variant="outlined" />
                                    <TextField id="outlined-basic" label="Optional" variant="outlined" />
                                </div>
                                
                            </div>
                            <div className="new-session-save">
                                <Button variant="contained" color="secondary" onClick={() => this.handleClose()}>Close</Button>
                                <Button style={{ marginLeft: 20 }} variant="contained" color="primary" onClick={() => this.handleSave()}>Save</Button>
                            </div>
                        </div>
                    </Dialog>
                </div>
            </div>
        )
    }
}