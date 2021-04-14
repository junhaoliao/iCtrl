const {spawn} = require("child_process")
const {IPC_SEND, IPC_RECV, send_msg} = require("./ipc")
const {Terminal} = require("xterm")
const {TransferManager} = require("./tf")


let SESSIONS = null

const TERM = new Terminal();
TERM.open(document.getElementById('terminal'));
TERM.onKey(async (e) => {
    const ev = e.domEvent;
    send_msg("send", {
        "s": "EECG1",
        "d": e.key
    })
});

function printLog(text) {
    const log_elem = document.getElementById("logs")
    const now = new Date()
    text = now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds() + ": " + text + "\n"
    if (log_elem) log_elem.innerText += text
}

function handle_sessions(value) {
    // TODO: integrated with GUI
    // printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)
    SESSIONS = value
}

function handle_login_ack(value){
    alert("Login: " + value)
}

function handle_recv(value){
    TERM.write(atob(value["d"]))
}

function handle_sftp_cwd(value){
    tf1.remote_cwd = value["dir"]
    tf1.fmUpdateAddrBar("remote")
    tf1.fmUpdateFileView("remote", value["files"])
}

function handle_main(key, value) {
    if (key === "sessions") {
        handle_sessions(value)
    }
    else if (key === "login_ack"){
        handle_login_ack(value)
    }
    else if (key === "recv"){
        handle_recv(value)
    }
    else if (key === "sftp_cwd"){
        handle_sftp_cwd(value)
    }
    else {
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
            if (!handle_main(key, recv_parsed[key])) {
                running = false
                break
            }
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    IPC_RECV.bind("tcp://*:8001").then(r => {
            printLog("Binding successful")

            const PyMotron = spawn(
                "../PyMotron/venv/bin/python3",
                [
                    "-u",
                    "../PyMotron/PyMotron.py",
                    8000,
                    8001
                ],
                {
                    cwd: "../PyMotron"
                });

            PyMotron.stdout.on("data", data => {
                printLog(`\nPyMotron stdout:\n ---\n ${data}---`);
            });

            PyMotron.stderr.on("data", data => {
                printLog(`\nPyMotron stderr:\n ---\n ${data}---`);
            });

            PyMotron.on('error', (error) => {
                printLog(`\nPyMotron error: ${error.message}`);
            });

            PyMotron.on("close", code => {
                printLog(`\nPyMotron exited with code ${code}`);
            });

            IPC_SEND.connect("tcp://127.0.0.1:8000")

            send_msg("sync")

            listen().then()
        }
    )
})

function debug_submit() {
    const debug_key = document.getElementById("debug_key")
    const debug_value = document.getElementById("debug_value")

    const debug_value_JSON = (debug_value.value === "")?null:JSON.parse(debug_value.value)

    send_msg(debug_key.value, debug_value_JSON)

    return false
}

const tf1 = new TransferManager("EECG1")
const local_homedir_files = tf1.localLs("")
tf1.fmUpdateAddrBar("local")
tf1.fmUpdateFileView("local", local_homedir_files)
