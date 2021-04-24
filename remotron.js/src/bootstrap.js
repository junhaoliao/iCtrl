const {spawn} = require("child_process")
const {createServer} = require("net")

const is_mac = process.platform === "darwin"
const PYTHON_PATH = is_mac ? "../PyMotron/venv/bin/python3" : "../PyMotron/venv/Scripts/python.exe"

function getFreePort() {
    const srv = createServer()
    srv.listen()
    const port = srv.address().port
    srv.close()
    return port
}

const SEND_PORT = getFreePort()
const RECV_PORT = getFreePort()

const PyMotron = spawn(
    PYTHON_PATH,
    [
        "-u",
        "../PyMotron/PyMotron.py",
        SEND_PORT,
        RECV_PORT
    ],
    {
        cwd: "../PyMotron"
    });