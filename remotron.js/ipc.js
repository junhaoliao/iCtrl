const ZMQ_CONTEXT = require("zeromq")

const IPC_RECV = new ZMQ_CONTEXT.Pull
const IPC_SEND = new ZMQ_CONTEXT.Push

module.exports.IPC_RECV = IPC_RECV
module.exports.IPC_SEND = IPC_SEND
module.exports.send_msg = send_msg

function send_msg(key, value=null) {
    const client_msg_json = {
        [key]: value
    }
    IPC_SEND.send(JSON.stringify(client_msg_json)).then()
}
