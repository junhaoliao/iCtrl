let SESSIONS = {}
let PROFILES = {}
let LOGINS = {}
let TERMS = {}
let TFS = {}

// let CONN_PROFILES = {}

function send_msg(key, value = null) {
    console.log(key, value)

    const client_msg_json = {
        [key]: value
    }
    console.log(client_msg_json)
    IPC_SEND.send(JSON.stringify(client_msg_json)).then()
}


function handle_sync_ack(value) {
    // console.log(value)
    // TODO: integrated with GUI
    // printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)
    PROFILES = value["profiles"]
    // console.log(PROFILES)

    SESSIONS = value["sessions"]
    for (const [session_name, session] of Object.entries(SESSIONS)) {
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
    semantic_flush_tabs()
    // console.log(SESSIONS)
}

function handle_profiles(value) {
    // TODO: integrated with GUI
    // printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)

    // value = conn_profiles
    buildNewTab(value)
}

function handle_login_ack(value) {
    alert("Login: " + value)
}

function handle_recv(value) {
    TERMS[value["s"]].write(atob(value["d"]))
}

function handle_sftp_cwd(value) {
    const session_name = value["session"]
    TFS[session_name].remote_cwd = value["dir"]
    TFS[session_name].fmUpdateAddrBar("remote")
    TFS[session_name].fmUpdateFileView("remote", value["files"])
}