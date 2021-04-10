const {spawn} = require("child_process");

const os = require("os")
const platform = os.platform()
let PYTHON_PATH = null
const PYMOTRON_PATH = "../PyMotron/PyMotron.py"
const CWD_PATH = "../PyMotron/"
if (platform === "win32"){
    PYTHON_PATH = "../PyMotron/venv/Scripts/python.exe"
} else if (platform === "darwin"){
    PYTHON_PATH = "../PyMotron/venv/bin/python3"
} else {
    alert("OS not supported "+ platform)
}

const ZMQ_CONTEXT = require("zeromq")
const IPC_RECV = new ZMQ_CONTEXT.Pull
const IPC_SEND = new ZMQ_CONTEXT.Push

const TERM = new Terminal();
TERM.open(document.getElementById('terminal'));
TERM.onKey(async (e) => {
    const ev = e.domEvent;
    IPC_SEND.send(JSON.stringify({"0": e.key})).then()
});

function printLog(text) {
    const log_elem = document.getElementById("logs")
    now = new Date()
    text = now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds() + ": " + text + "\n"
    if (log_elem) log_elem.innerText += text
}

function msg_generate(key, value = null) {
    return JSON.stringify({[key]: value})
}

function handle_sessions(value) {
    // TODO: integrated with GUI
    window.open('./debugger.html')
    printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)
}

function handle_terminal(value){
    // TODO: should add a parameter to allow reuse of this function for different terminals
    TERM.write(atob(value))
}

function handle_main(key, value) {
    if (key === "sessions") {
        handle_sessions(value)
    }
    else if (key === "0"){
        handle_terminal(value)
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
                PYTHON_PATH,
                [
                    "-u",
                    PYMOTRON_PATH,
                    8000,
                    8001
                ],
                {
                    cwd: CWD_PATH
                });

            PyMotron.stdout.on("data", data => {
                // printLog(`\nPyMotron stdout:\n ---\n ${data}---`);
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

            IPC_SEND.send(msg_generate("sync")).then()

            listen().then()
        }
    )
})

function debug_submit() {
    const debug_key = document.getElementById("debug_key")
    const debug_value = document.getElementById("debug_value")

    const debug_value_JSON = (debug_value.value === "")?null:JSON.parse(debug_value.value)

    IPC_SEND.send(msg_generate(debug_key.value, debug_value_JSON)).then()

    return false
}



