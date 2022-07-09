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
import {htmlResponseToReason} from './utils';

export const sftp_ls = (fm, path) => {
  // backup the old path for recovery when the ls fails
  const {cwd: oldCwd} = fm.state;

  fm.setState({
    loading: true,
    alertMsg: null,
    alertOpen: false,
  });
  axios.get(`/api/sftp_ls/${fm.session_id}`, {
    params: {
      path: path,
    },
  }).then(response => {
    const {files, cwd} = response.data;
    fm.setState({
      files: files,
      loading: false,
    });
    if (path[0] !== '/') {
      // only update cwd if path is in home dir
      fm.setState({
        cwd: cwd,
        cwdInput: cwd,
      });
    }
  }).catch(error => {
    fm.setState({
      cwd: oldCwd,
      cwdInput: oldCwd,
      loading: false,
    });
    if (error.response) {
      const reason = htmlResponseToReason(error.response.data, true);

      // if it is not a directory, I guess it is downloadable then?
      if (reason.startsWith('SFTPError(20,')) {
        let fileName = path.replace(oldCwd, '');
        if (fileName.charAt(0) === '/') {
          fileName = fileName.substring(1);
        }
        sftp_dl(fm.session_id, oldCwd, [fileName]);
      } else {
        fm.showAlert(reason);
      }
    } else {
      // Something happened in setting up the request that triggered an Error
      fm.showAlert('Error: ' + error.message);
    }
  });
};

export const sftp_dl = (session_id, cwd, files) => {
  window.location = `/api/sftp_dl/${session_id}?` +
      `cwd=${cwd}&` +
      `files=${JSON.stringify(files)}`;
};

export const sftp_ul = (fm, session_id, cwd, file, isDirectory) => {
  const uploadProgressIdx = fm.state.uploadProgress.length;
  const cancelTokenSrc = axios.CancelToken.source();
  fm.setState({
    uploadProgress: [
      ...fm.state.uploadProgress, {
        filename: file.name,
        progress: 0,
        speed: 0,
        loaded: 0,
        totalSize: file.size,
        cancelTokenSrc: cancelTokenSrc,
        cancelled: false,
      }],
  });
  const startTime = new Date().getTime();
  axios.post(
      `/api/sftp_ul/${session_id}`,
      file,
      {
        cancelToken: cancelTokenSrc.token,
        headers: {
          Cwd: cwd,
          Path: isDirectory ? (file.webkitRelativePath) : (file.name),
        },
        onUploadProgress: progressEvent => {
          const percentage = Math.floor(
              progressEvent.loaded * 100 / progressEvent.total);

          // the time is in milliseconds
          const speed = progressEvent.loaded *
              1000 / (new Date().getTime() - startTime);

          fm.setState(({uploadProgress}) => ({
            uploadProgress: [
              ...uploadProgress.slice(0, uploadProgressIdx),
              {
                ...uploadProgress[uploadProgressIdx],
                progress: percentage,
                speed: speed,
                loaded: progressEvent.loaded,
              },
              ...uploadProgress.slice(uploadProgressIdx + 1),
            ],
          }));
        },
      }).then(_ => {
    fm.loadDir(fm.state.cwd);
  }).catch(error => {
    if (error.response) {
      fm.showAlert(htmlResponseToReason(error.response.data));
    } else {
      // Something happened in setting up the request that triggered an Error
      fm.showAlert('Error: ' + error.message);
    }
  });
};

export const sftp_rename = (fm, session_id, cwd, old_name, new_name) => {
  axios.patch(`/api/sftp_rename/${session_id}`, {
    cwd: cwd,
    old: old_name,
    new: new_name,
  }).then(_ => {
    fm.loadDir(fm.state.cwd);
  }).catch(error => {
    console.log(error);
  });
};

export const sftp_rm = (fm, session_id, cwd, files) => {
  axios.post(`/api/sftp_rm/${session_id}`,
      {
        cwd: cwd,
        files: files,
      }).then(_ => {
    fm.loadDir(fm.state.cwd);
  }).catch(error => {
    fm.loadDir(fm.state.cwd);
    if (error.response) {
      fm.showAlert(htmlResponseToReason(error.response.data));
    } else {
      // Something happened in setting up the request that triggered an Error
      fm.showAlert('Error: ' + error.message);
    }
  });
};

export const sftp_chmod = (fm, cwd, name, mode, recursive) => {
  fm.setState({
    loading: true,
  });
  axios.patch(`/api/sftp_chmod/${fm.session_id}`, {
    path: `${cwd}/${name}`,
    mode: mode,
    recursive: recursive,
  }).then(_ => {
    fm.loadDir(cwd);
  }).catch(error => {
    fm.loadDir(cwd);
    if (error.response) {
      fm.showAlert(htmlResponseToReason(error.response.data));
    } else {
      // Something happened in setting up the request that triggered an Error
      fm.showAlert('Error: ' + error.message);
    }
  });
};

export const sftp_quota = (sessionID, ms) => {
  // load silently as much as possible
  // because not all machines support quota checking
  axios.post('/api/exec_blocking', {
    session_id: sessionID,
    cmd: 'quota -s | tail -n 1',
  }).then(res => {
    const mem = res.data.match(/[0-9]+[a-zA-Z]+/g);
    ms.setState({
      used: parseInt(mem[0]),
      usedUnit: mem[0].replace(/[0-9]+/, ''),
      quota: parseInt(mem[1]),
      quotaUnit: mem[1].replace(/[0-9]+/, ''),
    });
  }).catch(error => {
    // handle this silently because not all machines support quota checking
    ms.setState({quota: null});
  });
};

export const file_cleaner_rm = (session_id, files, cancelToken) => {
  axios.post(`/api/sftp_rm/${session_id}`,
      {
        cwd: '$HOME',
        files: files,
      }, {
        cancelToken,
      }).then(_ => {
    alert('The files have been deleted successfully. Press OK to reload.');
    window.location.reload();
  }).catch(error => {
    console.log(error);
    alert('Some files might NOT be deleted successfully. Press OK to reload.');
    // window.location.reload();
  });
};
