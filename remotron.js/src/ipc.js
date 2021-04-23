const net = require("net")
const {spawn} = require("child_process")
const {Pull, Push} = require("zeromq")

const platform = require("os").platform()
let PYTHON_PATH = null
if (platform === "darwin"){
    PYTHON_PATH = "../PyMotron/venv/bin/python3"
} else if (platform === "win32"){
    PYTHON_PATH = "../PyMotron/venv/Scripts/python.exe"
} else {
    alert("OS not supported "+ platform)
}

const IPC_RECV = new Pull
const IPC_SEND = new Push
module.exports.IPC_RECV = IPC_RECV
module.exports.IPC_SEND = IPC_SEND

const SEND_PORT = getFreePort()
const RECV_PORT = getFreePort()

function getFreePort() {
    const srv = net.createServer()
    srv.listen()
    const port = srv.address().port
    srv.close()
    return port
}

function handle_main(key, value) {
    if (key === "sync_ack") {
        handle_sync_ack(value)
    } else if (key === "profiles") {
        handle_profiles(value)
    } else if (key === "login_ack") {
        handle_login_ack(value)
    } else if (key === "recv") {
        handle_recv(value)
    } else if (key === "sftp_cwd") {
        handle_sftp_cwd(value)
    } else {
        printLog(`handle_main: Unknown key=${key}, value=${value}`)
        return false
    }

    return true
}

async function listen() {
    let running = true;
    while (running) {
        let recv_data = await IPC_RECV.receive()
        recv_data = recv_data.toString("utf-8")
        // printLog(recv_data)
        const recv_parsed = JSON.parse(recv_data)
        for (const key in recv_parsed) {
            // TODO: check why JetBrains is complaining about this
            if (!handle_main(key, recv_parsed[key])) {
                running = false
                break
            }
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    IPC_RECV.bind("tcp://*:"+String(RECV_PORT)).then(r => {
            console.log("Binding successful")

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

            PyMotron.stdout.on("data", data => {
                printLog(`\nPyMotron stdout:\n${data}`);
            });

            PyMotron.stderr.on("data", data => {
                printLog(`\nPyMotron stderr:\n${data}`);
            });

            PyMotron.on('error', (error) => {
                printLog(`\nPyMotron error: ${error.message}`);
            });

            PyMotron.on("close", code => {
                printLog(`\nPyMotron exited with code ${code}`);
            });

            IPC_SEND.connect("tcp://127.0.0.1:"+String(SEND_PORT))

            send_msg("sync")

            listen().then()
        }
    )
})

function debug_submit() {
    const debug_key = document.getElementById("debug_key")
    const debug_value = document.getElementById("debug_value")

    const debug_value_JSON = (debug_value.value === "") ? null : JSON.parse(debug_value.value)

    send_msg(debug_key.value, debug_value_JSON)

    return false
}