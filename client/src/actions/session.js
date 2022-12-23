/*
 * Copyright (c) 2021-2022 iCtrl Developers
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to
 *  deal in the Software without restriction, including without limitation the
 *  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 *  sell copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 *  IN THE SOFTWARE.
 */

import axios from 'axios';
import {sortListByKey} from './utils';

export const getAvatarName = (fullname) => {
  const hostname = fullname.split('.')[0];
  return hostname === '192' ? fullname.substr(-5, 5) : hostname;
};

export const session_ruptime = (cm, cancelToken) => {
  axios.post('/api/exec_blocking', {
    session_id: cm.props.session_id,
    cmd: 'ruptime -a | grep up', // TODO: review the need of '-a'
  }, {
    cancelToken: cancelToken,
  }).then(res => {
    // parse response data (str) into json format
    const machineList = [];
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
          machineList.push(machineJson);
        }
      }
    }

    // sort it before storing, now that x-data-grid doesn't support sorting with
    //  more than one conditions in the free version
    sortListByKey(machineList, 'load15');
    sortListByKey(machineList, 'load5');
    sortListByKey(machineList, 'load1');

    cm.setState({machineList});
  }).catch(error => {
    console.log(error);
  });
};

export const session_change_host = (sessionId, host, domain) => {
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

export const session_delete = sessionID => {
  axios.delete(`/api/session`, {
    params: {session_id: sessionID},
  }).then(response => {
    console.log(response.data);
    window.location.reload();
  }).catch(error => {
    console.log(error);
  });
};

export const session_change_nickname = (session, sessionID, nickname, host) => {
  axios.patch('/api/session', {
    session_id: sessionID,
    nickname: nickname,
  }).then(_ => {
    const _nickname = nickname === '' ? getAvatarName(host) : nickname;
    session.setState({
      nicknameChangeLoading: false,
      nickname: _nickname,
    });
    session.lastStoredNickname = _nickname;
  }).catch(error => {
    alert(error);
    window.location.reload();
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