// https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string/10420404
import * as constants from './constants';

export const humanFileSize = (size_in_bytes) => {
    const i = (size_in_bytes === 0) ? 0 : Math.floor(Math.log(size_in_bytes) / Math.log(1024));
    return (size_in_bytes / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
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