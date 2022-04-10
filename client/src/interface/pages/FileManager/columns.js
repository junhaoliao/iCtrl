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
