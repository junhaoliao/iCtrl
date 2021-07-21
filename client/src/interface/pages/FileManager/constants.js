/*
    https://raw.githubusercontent.com/torvalds/linux/
    5bfc75d92efd494db37f5c4c173d3639d4772966/include/uapi/linux/stat.h
*/
export const S_IFMT = 0o170000;
export const S_IFDIR = 0o40000;
export const S_IFLNK = 0o120000;
// export const S_IFREG = 0o100000;

export const S_IRUSR = 0o400;
export const S_IWUSR = 0o200;
export const S_IXUSR = 0o100;
export const S_IRGRP = 0o040;
export const S_IWGRP = 0o020;
export const S_IXGRP = 0o010;
export const S_IROTH = 0o004;
export const S_IWOTH = 0o002;
export const S_IXOTH = 0o001;

export const PERMISSION_BITS = [
    S_IRUSR,
    S_IWUSR,
    S_IXUSR,
    S_IRGRP,
    S_IWGRP,
    S_IXGRP,
    S_IROTH,
    S_IWOTH,
    S_IXOTH,
];