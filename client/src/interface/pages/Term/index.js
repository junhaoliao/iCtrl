import React from 'react';
import 'xterm/css/xterm.css';
import {sendKey, termConnect} from '../../../actions/term';
import {changeFavicon} from '../../utils';
import {TermSteps} from '../../components/Loading/steps';
import Loading from '../../components/Loading';
import Toolbar from '../../components/Toolbar';
import {isMobile} from '../../../actions/utils';
import {updateTitle} from '../../../actions/common';

export default class Term extends React.Component {
    constructor(props) {
        super(props);

        document.title = 'Terminal';

        const {match: {params}} = this.props;
        this.session_id = params.session_id;
        this.noLoadCheck = window.location.toString().includes('no_load_check');

        this.resize_timeout = null;

        this.ctrlKey = false;
        this.shiftKey = false;
        this.metaKey = false;
        this.altKey = false;

        this.state = {
            loading: true,
            currentStep: -1,
            authentication: null,
            isOverloaded: false
        };
    }

    handleToolbarSendKey = (key, down) => {
        this.term.focus();

        switch (key) {
            case 'Ctrl':
                this.ctrlKey = down;
                break;
            case 'Alt':
                this.altKey = down;
                break;
            case 'Shift':
                this.shiftKey = down;
                break;
            case '⌘':
                this.metaKey = down;
                break;

            case 'Tab':
                sendKey(this, {key: 'Tab', keyCode: 9});
                break;
            case 'Esc':
                sendKey(this, {key: 'Escape', keyCode: 27});
                break;
            case 'Delete':
                sendKey(this, {key: 'Delete', keyCode: 46});
                break;
            case 'Ctrl+Alt+Delete':
                console.log('Unexpected Ctrl+Alt+Delete pressed.');
                break;
            default:
                console.log('Unexpected key pressed.');
        }
    };

    componentDidMount() {
        updateTitle(this.session_id, 'Terminal');

        changeFavicon(`/api/favicon/terminal/${this.session_id}`);

        termConnect(this).then();
    }

    render() {
        const {authentication, currentStep, loading, isOverloaded} = this.state;

        return (
            <div>
                {loading &&
                <Loading
                    sessionId={this.session_id}
                    currentStep={currentStep}
                    steps={TermSteps}
                    authentication={authentication}
                    isOverloaded={isOverloaded}
                />}

                <div id="terminal" style={{
                    visibility: loading ? 'hidden' : 'visible',
                    position: 'absolute',
                    top: 0,
                    bottom: isMobile() ? 45 : 0,
                    left: 0,
                    right: 0,
                }}/>
                {isMobile() &&
                <Toolbar onToolbarSendKey={this.handleToolbarSendKey}/>
                }
            </div>
        );
    }
}