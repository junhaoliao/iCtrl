// TODO: add a Placeholder to signal the sessions are loading

const electron_ipc = require('electron').ipcRenderer
const {Session} = require("./session.js")

const rmt_tab_bar = document.getElementById("rmt_tab_bar")
const new_tab_button = document.getElementById("new_tab_button")

const pages_container = document.getElementById("pages_container")
const init_tab = document.getElementById("init_tab")

function semantic_toast(type, msg) {
    $("body")
      .toast({
        class: type,
        message: msg
      })
    ;
}

// TODO: refactor this func into a file
// This should be called after setting all loaded tabs
function semantic_flush_tabs() {
    $('.menu .item')
        .tab()
    ;
}

function _buildTab() {
    // remove the active tab's "active" class
    for (const tab of rmt_tab_bar.children) {
        tab.classList.remove("active")
    }
    for (const page of pages_container.children) {
        page.classList.remove("active")
    }

    // create new tab
    const new_tab = document.createElement("div")
    rmt_tab_bar.insertBefore(new_tab, new_tab_button)
    new_tab.innerText = "New Tab"
    new_tab.className = "active item rmt_tab"
    new_tab.setAttribute("data-tab", "NEW_TAB")

    const close_button = document.createElement("button")
    new_tab.appendChild(close_button)
    close_button.className = "ui circular icon button rmt_tab_close_button"
    close_button.onclick = () => {
        actCloseTab(new_tab, new_page)
    }

    const close_icon = document.createElement("i")
    close_button.appendChild(close_icon)
    close_icon.className = "icon close rmt_tab_close_icon"

    // create new page that corresponds to the tab
    const new_page = document.createElement("div")
    pages_container.appendChild(new_page)
    new_page.className = "ui bottom attached active tab rmt_page"
    new_page.setAttribute("data-tab", "NEW_TAB")

    return [new_tab, new_page]
}

function buildLoadedTab(session_name, profile_name, last_server, username, has_private_key, has_vnc_passwd) {
    // servers: Array(125), last_server: "ug250.eecg.toronto.edu", username: "liaojunh", private_key: false, vnc_manual: true
    const server_list = PROFILES["servers"]

    const loaded_tab_values = _buildTab()
    loaded_tab_values[0].firstChild.data = session_name
    loaded_tab_values[0].setAttribute("data-tab", session_name)

    const loaded_page = loaded_tab_values[1]
    loaded_page.setAttribute("data-tab", session_name)
    loaded_page.innerHTML = `
<div class="ui left fixed vertical labeled icon menu rmt_feature_menu">
    <a class="item active" data-tab="${session_name}-login">
        <i class="sign in icon"></i>
        Login
    </a>
    <a class="item " data-tab="${session_name}-terminal">
        <i class="terminal icon"></i>
        Terminal
    </a>
    <a class="item " data-tab="${session_name}-transfer">
        <i class="file outline icon"></i>
        Files
    </a>
</div>
<div id="${session_name}-login" class="ui active tab" data-tab="${session_name}-login"></div>
<div id="${session_name}-terminal" class="ui tab rmt_terminal" data-tab="${session_name}-terminal"></div>
<div id="${session_name}-tf" class="ui tab" data-tab="${session_name}-transfer"></div>
`
    SESSIONS[session_name] = new Session(session_name, profile_name)
    SESSIONS[session_name].loadFields(last_server, username, has_private_key, has_vnc_passwd)
}

function buildNewTab(connection_profiles) {
    new_tab_button.style.visibility = "hidden"
    const new_tab_values = _buildTab()
    const new_tab = new_tab_values[0]
    const new_page = new_tab_values[1]

    // TODO: use CSS to replace these
    new_page.appendChild(document.createElement("br"))
    new_page.appendChild(document.createElement("br"))
    new_page.appendChild(document.createElement("br"))

    const session_name_input_header = document.createElement("div")
    new_page.appendChild(session_name_input_header)
    session_name_input_header.innerText = "New Session Name"
    session_name_input_header.className = "ui medium header"

    const session_name_input_container = document.createElement("div")
    new_page.appendChild(session_name_input_container)
    session_name_input_container.className = "ui input"

    const session_name_input = document.createElement("input")
    session_name_input_container.appendChild(session_name_input)
    session_name_input.className = "rmt_session_name_input"
    session_name_input.type = "text"
    session_name_input.placeholder = "Please enter the new session name"

    // TODO: use CSS to replace these
    new_page.appendChild(document.createElement("br"))
    new_page.appendChild(document.createElement("br"))
    new_page.appendChild(document.createElement("br"))

    const connection_types_container = document.createElement("div")
    new_page.appendChild(connection_types_container)
    connection_types_container.className = "ui cards"

    for (const profile_name in connection_profiles){
        const connection_type = document.createElement("div")
        connection_types_container.appendChild(connection_type)
        connection_type.className = "card"
        connection_type.innerHTML = `
<div class="content">
    <div class="header">
    ${profile_name}
    </div>
</div>
<div class="extra content">
    <div class="ui two buttons">
        <div class="ui basic green button rmt_create_session_button" data-value="${profile_name}">Create</div>
        <div class="ui basic red button">Edit</div>
    </div>
</div>
`
    }
    const create_buttons = document.getElementsByClassName("rmt_create_session_button")
    // console.log(create_buttons)
    for (const button of create_buttons){
        button.onclick = ()=>{
            actAddNewSession(new_tab, new_page, button.getAttribute("data-value"), session_name_input)
        }
    }

    semantic_flush_tabs()
}

function destroyTab(tab, page) {
    if (tab.classList.contains("active")) {
        tab.previousElementSibling.classList.add("active")
        page.previousElementSibling.classList.add("active")
    }
    tab.remove()
    page.remove()

    semantic_flush_tabs()
}

function selectTab(tab_name) {
    // remove the active tab's "active" class
    for (const tab of rmt_tab_bar.children) {
        if (tab.getAttribute("data-tab") === tab_name){
            tab.classList.add("active")
        }
        else {
            tab.classList.remove("active")
        }
    }
    for (const page of pages_container.children) {
        if (page.getAttribute("data-tab") === tab_name){
            page.classList.add("active")
        }
        else {
            page.classList.remove("active")
        }
    }
}

// FIXME: revisit the need to put below code into a new file

const rmt_window_ctrl = document.createElement("div")
if (process.platform === "darwin"){
    rmt_tab_bar.insertBefore(rmt_window_ctrl, new_tab_button)
} else {
    rmt_tab_bar.appendChild(rmt_window_ctrl)
    rmt_window_ctrl.style.flexDirection = "row-reverse"
}
rmt_window_ctrl.id = "rmt_window_ctrl"
rmt_window_ctrl.className = "unselectable"
rmt_window_ctrl.innerHTML =
`
<div id="win_close_button" class="win_button">
    <a id="win_close_text" class="win_text">×</a>
</div>
<div id="win_min_button" class="win_button">
    <a id="win_min_text" class="win_text">－</a>
</div>
<div id="win_max_button" class="win_button">
    <a id="win_max_text" class="win_text">＋</a>
</div>
`

const win_close_button = document.getElementById("win_close_button")
win_close_button.onclick = ()=>{
    electron_ipc.send("close")
}
const win_min_button = document.getElementById("win_min_button")
win_min_button.onclick = ()=>{
    electron_ipc.send("min")
}
let fullscreen = false
const win_max_button = document.getElementById("win_max_button")
win_max_button.onclick = ()=>{
    if (process.platform === "darwin"){
        // in fullscreen mode, hide the min button on Mac
        fullscreen = !fullscreen
        win_min_button.style.visibility = fullscreen?"hidden":""
    }
    electron_ipc.send("max")
}


// FIXME: only uncomment this if the tabs are not able to load
//  at least the logs can be displayed if things have been wrong at the handshaking stage
// semantic_flush_tabs()

// semantic_toast("success", "Launched!")
