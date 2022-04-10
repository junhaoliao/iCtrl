import axios from 'axios';

export const session_ruptime = (cm, cancelToken) => {
  axios.post('/api/exec_blocking', {
    session_id: cm.props.session_id,
    cmd: 'ruptime -aur | grep up',
  }, {
    cancelToken: cancelToken,
  }).then(res => {
    // parse response data (str) into json format
    const machineListJson = [];
    for (const machine of res.data.split('\n')) {
      const machineInfo = machine.split(',');
      if (machineInfo.length === 5) {
        const host = machineInfo[0].split(' ')[0];

        // filter out the non-student hosts
        if (EECGHostList.includes(host) || ECFHostList.includes(host)) {
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
    console.log(error);
  });
};

export const session_change_host = (sessionId, host, domain) => {
  console.log(domain);
  axios.patch('/api/session', {
    session_id: sessionId,
    host: host,
    domain: domain,
  }).then(_ => {
    window.location.reload();
  }).catch(error => {
    console.log(error);
  });
};

const generateEECGHostList = () => {
  const list = [];

  // EECG Computers
  for (let i = 52; i <= 75; i++) {
    list.push(`ug${i}`);
  }
  for (let i = 132; i <= 180; i++) {
    list.push(`ug${i}`);
  }
  for (let i = 201; i <= 249; i++) {
    list.push(`ug${i}`);
  }

  return list;
};

const generateECFHostList = () => {
  const list = [];

  // ECF Computers
  for (let i = 1; i <= 185; i++) {
    list.push(`p${i}`);
  }
  list.push('remote');

  return list;
};

const EECGHostList = generateEECGHostList();
const ECFHostList = generateECFHostList();

const generateHostAddressList = () => {
  const list = [];

  list.push(
      ...EECGHostList.map((hostname) => (`${hostname}.eecg.toronto.edu`)));
  list.push(...ECFHostList.map((hostname) => (`${hostname}.ecf.utoronto.ca`)));

  return list;
};

export const hostAddressList = generateHostAddressList();