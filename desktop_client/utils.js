const {createServer} = require("net");

const getFreePort = () => {
    const srv = createServer()
    srv.listen()
    const port = srv.address()['port']
    srv.close()
    return port
}
exports.getFreePort = getFreePort

// https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string/10420404
const humanFileSize = (size_in_bytes) => {
    const i = (size_in_bytes === 0) ? 0 : Math.floor(Math.log(size_in_bytes) / Math.log(1024));
    return (size_in_bytes / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
};
exports.humanFileSize = humanFileSize
