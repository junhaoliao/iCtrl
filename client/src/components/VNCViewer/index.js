import React from 'react';
import RFB from '@novnc/novnc/core/rfb';
import axios from 'axios';


export default class FileManager extends React.Component {
    constructor(props) {
        super(props);
        const {
            match: {params},
            profiles: {sessions}
        } = props;

        this.session_id = params.session_id;
        this.username = sessions[this.session_id].username;
        this.host = sessions[this.session_id].host;
    }

    componentDidMount() {

        axios.post(`/vnc`, {
            session_id: this.session_id
        }).then(response=>{
            const {port, passwd} = response.data
            const url = `ws://localhost:${port}`
            // Creating a new RFB object will start a new connection
            const rfb = new RFB(
                document.getElementById('screen'),
                url,
                { credentials: { password: passwd } });
            rfb.resizeSession = true
            rfb.compressionLevel = 0
            // rfb.qualityLevel = 3
        }).catch(error=>{
            console.log(error)
        })


    }

    render() {
        return(<div style={{height:'100vh', width:'100vw'}} id={'screen'}/>);
    }
}