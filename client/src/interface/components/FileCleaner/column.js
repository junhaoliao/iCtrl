import {humanFileSize} from '../../pages/FileManager/utils';

const columns = [
  {
    field: 'size',
    headerName: 'Size',
    width: 100,
    valueFormatter: (params) => (humanFileSize(params.value)),
  },
  {
    field: 'id',
    headerName: 'File / Directory Name',
    flex: 1,
  },
];

export default columns;