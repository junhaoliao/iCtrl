// TODO: add a Placeholder to signal the sessions are loading

const {Terminal} = require("xterm")
const tab_bar = document.getElementById("tab_bar")
const new_tab_button = document.getElementById("new_tab_button")

const pages_container = document.getElementById("pages_container")
const init_page = document.getElementById("init_page")

// TODO: refactor this func into a file
// This should be called after setting all loaded tabs
function semantic_flush_tabs() {
    $('.menu .item')
        .tab()
    ;
}

function _buildTab() {
    // remove the active tab's "active" class
    for (const tab of tab_bar.children) {
        tab.classList.remove("active")
    }
    for (const page of pages_container.children) {
        page.classList.remove("active")
    }

    // create new tab
    const new_tab = document.createElement("div")
    tab_bar.insertBefore(new_tab, new_tab_button)
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

function test() {
    console.log(123)
}

function buildLoadedTab(session_name, profile_name, last_server, username, has_private_key, has_vnc_passwd) {
    // servers: Array(125), last_server: "ug250.eecg.toronto.edu", username: "liaojunh", private_key: false, vnc_manual: true
    const server_list = PROFILES["servers"]
    // TODO: modify here

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
    <a onclick="test()" class="item " data-tab="${session_name}-terminal">
        <i class="terminal icon"></i>
        Terminal
    </a>
    <a class="item " data-tab="${session_name}-transfer">
        <i class="file outline icon"></i>
        Files
    </a>
</div>
<div id="${session_name}-login" class="ui active tab" data-tab="${session_name}-login"></div>
<div id="${session_name}-terminal" class="ui tab" data-tab="${session_name}-terminal"></div>
<div id="${session_name}-tf" class="ui tab" data-tab="${session_name}-transfer"></div>
`
    // TODO: refactor those components into a class for easy init and destroy
    LOGINS[session_name] = new LoginPage(session_name, profile_name)
    LOGINS[session_name].loadFields(last_server, username, has_private_key, has_vnc_passwd)

    TERMS[session_name] = new Terminal()
    TERMS[session_name].open(document.getElementById(`${session_name}-terminal`))

    TERMS[session_name].onKey(async (e) => {
        send_msg("send", {
            "s": session_name,
            "d": e.key
        })
    });
    TFS[session_name] = new TransferManager(session_name)
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

semantic_flush_tabs()
