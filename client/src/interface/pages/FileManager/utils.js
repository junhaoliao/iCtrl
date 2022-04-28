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

import * as constants from './constants';

// https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string/10420404
export const humanFileSize = (size_in_bytes) => {
  const i = (size_in_bytes === 0) ?
      0 :
      Math.floor(Math.log(size_in_bytes) / Math.log(1024));
  return (size_in_bytes / Math.pow(1024, i)).toFixed(2) * 1 + ' ' +
      ['B', 'KB', 'MB', 'GB', 'TB'][i];
};

export const isDir = (mode) => {
  return (parseInt(mode) & constants.S_IFMT) === constants.S_IFDIR;
};
export const isLnk = (mode) => {
  return (parseInt(mode) & constants.S_IFMT) === constants.S_IFLNK;
};

export const dateFormatter = (params) => {
  const theDate = new Date(params.value * 1000);
  const dateOptions = {year: 'numeric', month: 'short', day: 'numeric'};
  const timeOptions = {hour: '2-digit', minute: '2-digit'};

  return `${theDate.toLocaleDateString('en-US', dateOptions)} 
                        at ${theDate.toLocaleTimeString('en-US', timeOptions)}`;
};

export const permissionFormatter = (params) => {
  const mode = parseInt(params.value);
  const mode_str_arr = [
    (mode & constants.S_IFDIR) ? 'd' : '-',
    (mode & constants.S_IRUSR) ? 'r' : '-',
    (mode & constants.S_IWUSR) ? 'w' : '-',
    (mode & constants.S_IXUSR) ? 'x' : '-',
    (mode & constants.S_IRGRP) ? 'r' : '-',
    (mode & constants.S_IWGRP) ? 'w' : '-',
    (mode & constants.S_IXGRP) ? 'x' : '-',
    (mode & constants.S_IROTH) ? 'r' : '-',
    (mode & constants.S_IWOTH) ? 'w' : '-',
    (mode & constants.S_IXOTH) ? 'x' : '-',
  ];
  return mode_str_arr.join('');
};