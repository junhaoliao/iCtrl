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

import {Stack} from '@mui/material';
import {ShortcutIcon} from '../../../icons';
import FolderIcon from '@mui/icons-material/Folder';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import {
  dateFormatter,
  humanFileSize,
  isDir,
  isLnk,
  permissionFormatter,
} from './utils';
import React from 'react';

import '../../../index.css';

const columns = [
  {
    field: 'id', headerName: 'Name', flex: 1, minWidth: 200,
    renderCell: (params) => {
      const is_dir = isDir(params.getValue(params.value, 'mode'));
      const is_lnk = isLnk(params.getValue(params.value, 'mode'));
      return (
          <Stack direction={'row'} spacing={1}>
            <div style={{position: 'relative', top: 5}}>
              {is_lnk ?
                  <ShortcutIcon/> :
                  (is_dir ? <FolderIcon fontSize={'small'}/> :
                      <InsertDriveFileIcon fontSize={'small'}/>)}
            </div>
            <div>{params.value}</div>
          </Stack>

      );
    },
  },
  {
    field: 'size', headerName: 'Size', width: 100,
    valueFormatter: (params) => (humanFileSize(params.value)),
  },
  {
    field: 'atime', headerName: 'Date Accessed', width: 190,
    valueFormatter: dateFormatter,
  },
  {
    field: 'mtime', headerName: 'Date Modified', width: 190,
    valueFormatter: dateFormatter,
  },
  {
    field: 'mode', headerName: 'Permission', width: 132,
    valueFormatter: permissionFormatter,
  },
];
export default columns;
