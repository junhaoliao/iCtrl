const {spawn} = require("child_process")
const {createServer} = require("net")

const is_mac = process.platform === "darwin"
let PYTHON_PATH = null
let CWD = "."
if (is_mac){
    if (process.env.npm_node_execpath === "/usr/local/bin/node"){
        PYTHON_PATH = "venv/bin/python3"
    } else {
        const {resolve} = require("path")
        PYTHON_PATH = resolve(__dirname, "../venv/bin/python3")
        CWD = resolve(__dirname, "..")
    }
} else {
    PYTHON_PATH = "venv/Scripts/python.exe"
}

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
        "libugremote/PyMotron.py",
        SEND_PORT,
        RECV_PORT
    ],
    {
        cwd: CWD
    });