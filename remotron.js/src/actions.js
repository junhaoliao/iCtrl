function actOpenNewTab() {
    send_msg("query_profiles")
}

function actAddNewSession(tab, page, profile_name, session_name_input) {
    const session_name = session_name_input.value
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

    new_tab_button.style.visibility = ""
}

function actCloseTab(tab, page) {
    // TODO: should terminate the session on the server side as well
    destroyTab(tab, page)
}