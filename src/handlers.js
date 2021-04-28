let PROFILES = {}
const SESSIONS = {}

// let CONN_PROFILES = {}

function send_msg(key, value = null) {
    // console.log(key, value)

    const client_msg_json = {
        [key]: value
    }
    // console.log(client_msg_json)
    IPC_SEND.send(JSON.stringify(client_msg_json)).then()
}

function handle_sync_ack(value) {
    // console.log(value)
    // TODO: integrated with GUI
    // printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)
    PROFILES = value["profiles"]
    // console.log(PROFILES)

    // SESSIONS =
    for (const [session_name, session] of Object.entries(value["sessions"])) {
        // buildLoadedTab(session_name, profile_name, last_server, username, has_private_key, has_vnc_passwd)
        buildLoadedTab(
            session_name,
            session["profile"],
            session["last_server"],
            session["username"],
            session["private_key"],
            session["vnc_passwd"]
        )
    }
    selectTab(value["last_session"])
    semantic_flush_tabs()
    semantic_flush_dropdowns()
    // console.log(SESSIONS)
    const {ipcRenderer} = require("electron")
    ipcRenderer.send("profiler_sync_ack")
}

function handle_profiles(value) {
    // TODO: integrated with GUI
    // printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)

    // value = conn_profiles
    buildNewTab(value)
}

function handle_login_ack(value) {
    // value is session_name
    // alert("Login: " + value)
    // TODO: think about a better way to support message types (error, success, warning)
    if (value.includes("Failed")) {
        semantic_toast("error", value)
    } else {
        semantic_toast("success", value)
        // const login_menu_button = document.getElementById(`${session_name}-login_menu_button`)
        const term_menu_button = document.getElementById(`${value}-term_menu_button`)
        term_menu_button.classList.remove("disabled")
        const tf_menu_button = document.getElementById(`${value}-tf_menu_button`)
        tf_menu_button.classList.remove("disabled")
    }

}

function handle_recv(value) {
    const term = SESSIONS[value["s"]].term
    if (!term.fitted){
        term.fit()
        term.fitted = true
    }
    term.terminal.write(atob(value["d"]))
}

function handle_sftp_cwd(value) {
    const session_name = value["session"]
    SESSIONS[session_name].tf.remote_cwd = value["dir"]
    SESSIONS[session_name].tf.fmUpdateAddrBar("remote")
    SESSIONS[session_name].tf.fmUpdateFileView("remote", value["files"])
}