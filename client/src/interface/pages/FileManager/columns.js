import {Stack} from '@material-ui/core';
import {ShortcutIcon} from '../../../icons';
import FolderIcon from '@material-ui/icons/Folder';
import InsertDriveFileIcon from '@material-ui/icons/InsertDriveFile';
import {dateFormatter, humanFileSize, isDir, isLnk, permissionFormatter} from './utils';
import React from 'react';

import '../../../index.css';

const columns = [
    {
        field: 'id', headerName: 'Name', flex: 1,
        renderCell: (params) => {
            const is_dir = isDir(params.getValue(params.value, 'mode'));
            const is_lnk = isLnk(params.getValue(params.value, 'mode'));
            return (
                <Stack className={'no_select'} direction={'row'} spacing={1}>
                    <div style={{position: 'relative', top: 5}}>
                        {is_lnk ? <ShortcutIcon/> : (is_dir ? <FolderIcon fontSize={'small'}/> :
                            <InsertDriveFileIcon fontSize={'small'}/>)}
                    </div>
                    <div>{params.value}</div>
                </Stack>

            );
        }
    },
    {
        field: 'size', headerName: 'Size', width: 90,
        valueFormatter: (params) => (humanFileSize(params.value))
    },
    {
        field: 'atime', headerName: 'Date Accessed', width: 186,
        valueFormatter: dateFormatter
    },
    {
        field: 'mtime', headerName: 'Date Modified', width: 186,
        valueFormatter: dateFormatter
    },
    {
        field: 'mode', headerName: 'Permission', width: 132,
        valueFormatter: permissionFormatter
    },
];
export default columns;
