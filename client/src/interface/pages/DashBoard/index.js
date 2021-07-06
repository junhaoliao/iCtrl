/* eslint-disable react-hooks/rules-of-hooks */
import React from 'react';
import NewSession from '../../components/NewSession';
import ChangeMachine from '../../components/ChangeMachine';

import './index.css';

export default class DashBoard extends React.Component {
    constructor(props) {
        super(props);
        this.state ={
            activeTab: 0,
            data: {},
            addNewSession: false,
            changeMachine: false,
        }
    }

    componentDidMount() {
        const data = {
            "last_session": "4502c2b1a51c41b2ad3a6a1c7e9a188f",
            "sessions": {
                "4502c2b1a51c41b2ad3a6a1c7e9a188f": {
                    "host": "ictrl.ca",
                    "username": "root"
                }
            },
            "version": 1,
            "viewer": "TigerVNC"
        };
        this.setState({ data });
    }

    handleAddNewSession() {
        console.log('ready to add session');
        this.handleNewSessionMask();
    }

    handleNewSessionMask() {
        const { addNewSession } = this.state;
        this.setState({ addNewSession: !addNewSession});
    }

    handleChangeMachine() {
        const { changeMachine } = this.state;
        this.setState({ changeMachine: !changeMachine});
    }

    handleBtnClick(uuid, type) {
        console.log('current type is: ', type, ' and uuid is: ', uuid);
        switch (type) {
            case 'cm':
                this.handleChangeMachine();
                break;
            case 'vnc':
                window.open(`/vnc/${uuid}`, '_blank');
                break;
            case 'term':
                window.open(`/terminal/${uuid}`, '_blank');
                break;
            case 'file':
                window.open(`/fm/${uuid}`, '_blank');
                break;
            case 'more':
                break;
            default: return;
        }
    }

    render() {
        const { data, addNewSession, changeMachine } = this.state;
        const sessionList = [];
        if (data.sessions) {
            // console.log(data)
            for (const [key, value] of Object.entries(data.sessions)) {
                console.log(key, value.host, value.username);
                const session = (
                    <div className="dashboard-single-session">
                        <div className="dashboard-text-wrapper">
                            <div className="dashboard-session-host">{value.host}</div>
                            <div className="dashboard-session-username">{value.username}</div>
                        </div>
                        <div className="dashboard-session-btn-wrapper">
                            <div className="dashboard-session-btn" onClick={() => this.handleBtnClick(key, 'cm')}>CM</div>
                            <div className="dashboard-session-btn" onClick={() => this.handleBtnClick(key, 'vnc')}>VNC</div>
                            <div className="dashboard-session-btn" onClick={() => this.handleBtnClick(key, 'term')}>{'>-'}</div>
                            <div className="dashboard-session-btn" onClick={() => this.handleBtnClick(key, 'file')}>File</div>
                            <div className="dashboard-session-btn" onClick={() => this.handleBtnClick(key, 'more')}>...</div>
                        </div>
                    </div>
                );
                sessionList.push(session);
            }
        }
        return (
            <div className="dashboard-wrapper">ChangeMachine
                {addNewSession ? <NewSession handleDone={() => this.handleNewSessionMask()} /> : null}
                {changeMachine ? <ChangeMachine handleDone={() => this.handleChangeMachine()} /> : null}
                <div className="dashboard-title-wrapper">
                    <div className="dashboard-tab">DashBoard</div>
                    <div className="dashboard-add-btn" onClick={() => this.handleAddNewSession()}>
                        +
                    </div>
                </div>

                <div className="dashboard-sessions-wrapper">
                    {sessionList}
                </div>
            </div>
        )
    }
}