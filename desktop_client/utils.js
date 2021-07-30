const {createServer} = require("net");

const getFreePort = () => {
    const srv = createServer()
    srv.listen()
    const port = srv.address()['port']
    srv.close()
    return port
}
exports.getFreePort = getFreePort

