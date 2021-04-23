class LoginPage{
    session_name = null
    use_private_key = null

    constructor(session_name, profile_name) {
        this.session_name = session_name

        // const login_page =

        const login_div = document.getElementById(`${session_name}-login`)
        // TODO: replace these <br> with CSS
        // TODO: refactor the styles into CSS
        login_div.innerHTML = `
<br>
<br>
<br>
<br>
<div class="ui placeholder segment" style="width: 640px; margin-left: auto; margin-right: auto">
    <div class="ui two column grid">
        <div class="column">
            <form id="${session_name}-login_form" class="ui form">
                <div class="field">
                    <label>Username</label>
                    <div class="ui left icon input">
                        <input id="${session_name}-username" placeholder="Username" type="text">
                        <i class="user icon"></i>
                    </div>
                </div>
                <div class="field">
                    <label>Password</label>
                    <div class="ui left icon input">
                        <input id="${session_name}-password" placeholder="Password" type="password">
                        <i class="lock icon"></i>
                    </div>
                </div>
                <div class="field">
                    <label>Server</label>
                    <select id="${session_name}-server_dropdown" class="ui search dropdown">
                      <option value="">Select Server</option>
                    </select>
                </div>
                <button class="ui blue button" type="submit">Login</button>
            </form>
        </div>
        <div class="column">
            <div class="ui form">
                <div class="field">
                    <label>Reset VNC</label>
                    <div class="ui slider checkbox" style="margin-top: 12px; margin-bottom: 6px">
                        <input name="newsletter" type="checkbox">
                        <label>Reset the VNC</label>
                    </div>
                </div>
                <div class="field">
                    <label>New VNC Password</label>
                    <div class="ui left icon input">
                        <input placeholder="New password" type="text">
                        <i class="lock icon"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="ui vertical divider">
        ${profile_name}
    </div>
</div>
    `
        const server_dropdown = document.getElementById(`${session_name}-server_dropdown`)
        for (const server of PROFILES[profile_name]["servers"]){
            const server_option = document.createElement("option")
            server_dropdown.appendChild(server_option)
            server_option.value = server
            server_option.innerText = server
        }
        $(".dropdown").dropdown()

        // register login callback
        const login_form = document.getElementById(`${session_name}-login_form`)
        login_form.onsubmit = ()=>{
            return this.actLogin()
        }
    }
    loadFields(last_server, username, has_private_key, has_vnc_passwd){
        const server_dropdown = document.getElementById(`${this.session_name}-server_dropdown`)
        server_dropdown.value = last_server
        const username_input = document.getElementById(`${this.session_name}-username`)
        username_input.value = username

        this.use_private_key = has_private_key
        if (has_private_key){
            const password_input = document.getElementById(`${this.session_name}-password`)
            password_input.value = "********"
        }
        // TODO: handle has_vnc_passwd
        // if (has_vnc_passwd){
        //     const vncpass = document.getElementById(`${this.session_name}-password`)
        //     password_input.value = "********"
        // }

    }
    actLogin(){
        const server = document.getElementById(`${this.session_name}-server_dropdown`).value
        const username = document.getElementById(`${this.session_name}-username`).value
        const password = document.getElementById(`${this.session_name}-password`).value
        const value = {
            "session": this.session_name,
            "server": server,
            "username": username,
            "passwd": password,
            "save_key": false
        }
        send_msg("login", value)
        return false
    }
    
    actDisconnect(){
        
    }
}
module.exports.LoginPage = LoginPage