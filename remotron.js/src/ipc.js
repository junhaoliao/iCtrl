const {Pull, Push} = require("zeromq")

const IPC_RECV = new Pull
const IPC_SEND = new Push
module.exports.IPC_RECV = IPC_RECV
module.exports.IPC_SEND = IPC_SEND

IPC_RECV.bind("tcp://*:" + String(RECV_PORT)).then(() => {
    console.log("Binding successful")
    IPC_SEND.connect("tcp://127.0.0.1:" + String(SEND_PORT))
    send_msg("sync")
    listen().then()
})

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