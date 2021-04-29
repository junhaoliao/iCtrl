function actOpenNewTab() {
    if (Object.keys(SESSIONS).length>=5){
        semantic_toast("error", `Cannot open more than 5 tabs.`)
    } else{
        send_msg("query_profiles")
    }
}

function actAddNewSession(tab, page, profile_name, session_name_input) {
    const session_name = session_name_input.value
    if (session_name in SESSIONS) {
        semantic_toast("error", `Already has a session named "${session_name}"`)
        return
    } else if (session_name === "") {
        // TODO: generate a name according to the profile name
        semantic_toast("error", `Session name cannot be empty`)
        return
    }

    send_msg("new_session", {
        "profile": profile_name,
        "session": session_name
    })
    tab.remove()
    page.remove()
    buildLoadedTab(
        session_name,
        profile_name,
        "",
        "",
        false,
        false
    )
    semantic_flush_tabs()
    semantic_flush_dropdowns()

    new_tab_button.style.visibility = ""
}

function actCloseTab(tab, page) {
    if ("NEW_TAB" === tab.getAttribute("data-tab")) {
        new_tab_button.style.visibility = ""
    }

    // FIXME: should terminate the session on the server side as well
    delete SESSIONS[tab.getAttribute("data-tab")]
    destroyTab(tab, page)
}