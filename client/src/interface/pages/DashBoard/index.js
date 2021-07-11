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
            data: props.profiles,
            addNewSession: false,
            changeMachine: false,
        }
    }

    componentDidMount() {
        console.log(this.state.data, this.props.profiles)
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

    handleBtnClick(sessionId, type) {
        // console.log('current type is: ', type, ' and sessionId is: ', sessionId);
        this.setState({ sessionId });
        switch (type) {
            case 'cm':
                this.handleChangeMachine();
                break;
            case 'vnc':
                window.open(`/vnc/${sessionId}`, '_blank');
                break;
            case 'term':
                window.open(`/terminal/${sessionId}`, '_blank');
                break;
            case 'file':
                window.open(`/fm/${sessionId}`, '_blank');
                break;
            case 'more':
                break;
            default: return;
        }
    }

    render() {
        const { data, addNewSession, changeMachine } = this.state;
        const sessionList = [];
        //{
        //     "last_session": "4502c2b1a51c41b2ad3a6a1c7e9a188f",
        //     "sessions": {
        //         "4502c2b1a51c41b2ad3a6a1c7e9a188f": {
        //             "host": "ictrl.ca",
        //             "username": "root"
        //         }
        //     },
        //     "version": 1,
        //     "viewer": "TigerVNC"
        // };
        if (data.sessions) {
            for (const [key, value] of Object.entries(data.sessions)) {
                const showCM = value.host.endsWith('toronto.edu');
                const session = (
                    <div className="dashboard-single-session" key={key} >
                        <div className="dashboard-text-wrapper">
                            <div className="dashboard-session-host">{value.host}</div>
                            <div className="dashboard-session-username">{value.username}</div>
                        </div>
                        <div className="dashboard-session-btn-wrapper">
                            {showCM && <div className="dashboard-session-btn" onClick={() => this.handleBtnClick(key, 'cm')}>CM</div>}
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
                {changeMachine ? <ChangeMachine sessionId={this.state.sessionId} handleDone={() => this.handleChangeMachine()} /> : null}
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