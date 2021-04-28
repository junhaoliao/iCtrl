const {LoginPage} = require("./login.js")
const {Term} = require("./term.js")
const {TransferManager} = require("./tf.js")

class Session {
    login = null
    term = null
    tf = null
    // TODO: add vnc
    vnc = null

    constructor(session_name, profile_name) {
        if (session_name in SESSIONS) {
            console.log("already in session")
        }
        this.login = new LoginPage(session_name, profile_name)
        this.term = new Term(session_name)
        this.tf = new TransferManager(session_name)

        // const login_menu_button = document.getElementById(`${session_name}-login_menu_button`)
        const term_menu_button = document.getElementById(`${session_name}-term_menu_button`)
        // console.log(term_menu_button)
        // term_menu_button.addEventListener("click", ()=>{
        //
        // })
        term_menu_button.onclick = ()=>{
            console.log(this.term.activated)
            if (!this.term.activated){
                send_msg("shell", session_name)
                this.term.activated = true
            }
        }
        // const tf_menu_button = document.getElementById(`${session_name}-tf_menu_button`)
    }

    loadFields(last_server, username, has_private_key, has_vnc_passwd) {
        this.login.loadFields(last_server, username, has_private_key, has_vnc_passwd)
    }


}

module.exports.Session = Session