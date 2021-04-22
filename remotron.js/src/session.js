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
        if (session_name in SESSIONS){
            console.log("already in session")
        }
        this.login = new LoginPage(session_name, profile_name)
        this.term = new Term(session_name)
        this.tf = new TransferManager(session_name)
    }
    loadFields(last_server, username, has_private_key, has_vnc_passwd){
        this.login.loadFields(last_server, username, has_private_key, has_vnc_passwd)
    }
}
module.exports.Session = Session