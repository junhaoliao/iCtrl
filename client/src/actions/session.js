import axios from 'axios';

export const session_ruptime = (sessionId, cm) => {
    axios.post('/exec_blocking', {
        session_id: sessionId,
        cmd: 'ruptime -aur | grep up'
    }).then(res => {
        // parse response data (str) into json format
        const machineListJson = [];
        for (const machine of res.data.split('\n')) {
            const machineInfo = machine.split(',');
            if (machineInfo.length === 5) {
                const host = machineInfo[0].split(' ')[0];

                // filter out the non-student hosts
                if (host.match(/^ug\d+/) || host.match(/^p\d+/) || host === 'remote') {
                    const machineJson = {
                        'id': host,
                        'userNum': parseInt(machineInfo[1]),

                        // no need to convert the loads to float as we want to display the last 2 digits anyways
                        // e.g. 0.00
                        'load1': machineInfo[2].match(/[0-9]+.[0-9]+/),
                        'load5': machineInfo[3],
                        'load15': machineInfo[4],
                    };
                    machineListJson.push(machineJson);
                }
            }
        }
        cm.setState({machineList: machineListJson});
    }).catch(error => {
        cm.setState({machineList: null});
    });
};

export const session_change_host = (sessionId, host, domain) => {
    console.log(domain)
    axios.patch('/session', {
        session_id: sessionId,
        host: `${host}${domain}`
    }).then(_ => {
        window.location.reload();
    }).catch(error => {
        console.log(error);
    });
};
