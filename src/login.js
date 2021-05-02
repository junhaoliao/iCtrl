class LoginPage {
    session_name = null
    profile_name = null
    use_private_key = null

    constructor(session_name, profile_name) {
        this.session_name = session_name
        this.profile_name = profile_name

        // const login_page =

        const login_div = document.getElementById(`${session_name}-login`)
        // TODO: replace these <br> with CSS
        // TODO: refactor the styles into CSS
        login_div.innerHTML = `
<div id="${session_name}-steps" class="ui three steps">
  <div id="${this.session_name}-step-login" class="active step">
    <i class="user icon"></i>
    <div class="content">
      <div class="title">Login</div>
      <div class="description">Enter your credentials</div>
    </div>
  </div>
  <div id="${this.session_name}-step-utils" class="disabled step">
    <i class="desktop icon"></i>
    <div class="content">
      <div class="title">Utils</div>
      <div class="description">Change Machine or Launch VNC</div>
    </div>
  </div>
  <div id="${this.session_name}-step-vncopt" class="disabled step">
    <i class="key icon"></i>
    <div class="content">
      <div class="title">VNC Options</div>
      <div class="description">Set VNC password if needed</div>
    </div>
  </div>
</div>
<br>
<br>
<br>
<br>
<div style="width: 500px; margin: auto">
<div id="${session_name}-sides" class="ui shape" style="width: 100%">
  <div class="sides">
    <div id="${session_name}-side-login" class="active side">
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
        <div class="field">
            <div class="ui toggle checkbox">
                <input id="${session_name}-save_key" type="checkbox">
                <label>Remember Password</label>
            </div>
        </div>
        <button class="ui blue button" type="submit">Login</button>
    </form>
    </div>
    <div id="${session_name}-side-utils" class="side">
    <form id="${session_name}-vnc_form" class="ui form">
        <button class="ui yellow button" type="submit">Connect VNC</button>
    </form>
    </div>
    <div id="${session_name}-side-vncopt" class="side">
    <form id="${session_name}-form-vncopt" class="ui form">
        <div class="field">
            <label>VNC Password</label>
            <div class="ui left icon input">
                <input id="${session_name}-vnc_passwd" placeholder="VNC Password" type="password">
                <i class="lock icon"></i>
            </div>
        </div>
        <button class="ui yellow button" type="submit">Connect VNC</button>
    </form>
    </div>
  </div>
</div>
</div>

    `
        // TODO: refactor this
        $(`#${session_name}-sides`).shape();

        const server_dropdown = document.getElementById(`${session_name}-server_dropdown`)
        // const empty_server_option = document.createElement("option")
        // server_dropdown.appendChild(empty_server_option)
        // empty_server_option.value = " "
        for (const server of PROFILES[profile_name]["servers"]) {
            const server_option = document.createElement("option")
            server_dropdown.appendChild(server_option)
            server_option.value = server
            server_option.innerText = server
        }

        // register login callback
        const login_form = document.getElementById(`${session_name}-login_form`)
        login_form.onsubmit = () => {
            return this.actLogin()
        }

        // register vnc callback
        const vnc_form = document.getElementById(`${session_name}-vnc_form`)
        vnc_form.onsubmit = () => {
            return this.actVNC()
        }

        const vncopt_form = document.getElementById(`${session_name}-form-vncopt`)
        vncopt_form.onsubmit = () => {
            const vncpasswd = document.getElementById(`${session_name}-vnc_passwd`).value
            return this.actVNC(vncpasswd)
        }
    }

    loadFields(last_server, username, has_private_key, has_vnc_passwd) {
        const server_dropdown = document.getElementById(`${this.session_name}-server_dropdown`)
        server_dropdown.value = last_server
        const username_input = document.getElementById(`${this.session_name}-username`)
        username_input.value = username

        this.use_private_key = has_private_key
        if (has_private_key) {
            const password_input = document.getElementById(`${this.session_name}-password`)
            password_input.setAttribute("placeholder", "●●●●●●●●")
            const save_key_checkbox = document.getElementById(`${this.session_name}-save_key`)
            save_key_checkbox.checked = true
        }
        // TODO: handle has_vnc_passwd
        // if (has_vnc_passwd){
        //     const vncpass = document.getElementById(`${this.session_name}-password`)
        //     password_input.value = "********"
        // }

    }

    actLogin() {
        const server = document.getElementById(`${this.session_name}-server_dropdown`).value
        console.log(server)
        if (server === "") {
            // pick a random server if the user doesn't input one
            const server_elem = document.getElementById(`${this.session_name}-server_dropdown`)
            const servers_list = PROFILES[this.profile_name]["servers"]
            server_elem.value = servers_list[Math.floor(Math.random() * servers_list.length)]
            semantic_flush_dropdowns()
        }
        const username = document.getElementById(`${this.session_name}-username`).value
        const password = document.getElementById(`${this.session_name}-password`).value
        const save_key = document.getElementById(`${this.session_name}-save_key`).checked
        const value = {
            "session": this.session_name,
            "server": server,
            "username": username,
            "passwd": password,
            "save_key": save_key
        }
        send_msg("login", value)
        return false
    }

    actVNC(vncpasswd=null){
        const value = {
            "session": this.session_name,
            "passwd": vncpasswd
        }
        send_msg("vnc", value)

        return false
    }

    actDisconnect() {

    }

    setStep(step_name){
        // console.log(`#${this.session_name}-step-${step_name}`)
        const steps = document.getElementById(`${this.session_name}-steps`)
        for (const this_step of steps.children){
            this_step.classList.remove("active")

            if (this_step.id === `${this.session_name}-step-${step_name}`){
                this_step.classList.remove("disabled")
                this_step.classList.add("active")
            }
        }

        $(`#${this.session_name}-sides`)
        .shape('set next side', `#${this.session_name}-side-${step_name}`)
        .shape('flip right')
        ;
    }
}

module.exports.LoginPage = LoginPage