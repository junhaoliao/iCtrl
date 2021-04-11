const {spawn} = require("child_process");


const os = require("os")
const platform = os.platform()
let PYTHON_PATH = null
const PYMOTRON_PATH = "../PyMotron/PyMotron.py"
const CWD_PATH = "../PyMotron/"
if (platform === "win32"){
    PYTHON_PATH = "../PyMotron/venv/Scripts/python.exe"
} else if (platform === "darwin"){
    PYTHON_PATH = "../PyMotron/venv/bin/python3"
} else {
    alert("OS not supported "+ platform)
}

const ZMQ_CONTEXT = require("zeromq")
const IPC_RECV = new ZMQ_CONTEXT.Pull
const IPC_SEND = new ZMQ_CONTEXT.Push

let SESSIONS = null

function send_msg(key, value=null) {
    const client_msg_json = {
        [key]: value
    }
    IPC_SEND.send(JSON.stringify(client_msg_json)).then()
}


const TERM = new Terminal();
TERM.open(document.getElementById('terminal'));
TERM.onKey(async (e) => {
    const ev = e.domEvent;
    send_msg("send", {
        "s": "EECG1",
        "d": e.key
    })
});

function printLog(text) {
    const log_elem = document.getElementById("logs")
    const now = new Date()
    text = now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds() + ": " + text + "\n"
    if (log_elem) log_elem.innerText += text
}

function handle_new_session(value) {
    const EECG = value.EECG1;
    const ECF = value.ECF1;
    console.log(value, EECG, ECF)
    const log_elem = document.getElementById("pop-up-menu-address")
    document.getElementById('username').value = EECG.username
    // document.getElementById('password').value = EECG.password
    const selector = document.getElementById('pop-up-display-address')
    selector.innerHTML = EECG.last_server
    selector.style.color = '#242424'
    EECG.servers.map((item, index) => {
        const id = `server-${index}`
        const dom = document.createElement("div")
        dom.className = 'item'
        // dom.setAttribute('data-value', index)
        dom.id = id
        dom.onclick = () => {
          chooseConnect(id, 'address')
        }
        // dom.setAttribute('id', id)
        // dom.setAttribute('onclick', "chooseConnect(id, 'address');")
        dom.innerText = item
        // const lalala = `<div class="item" data-value="${index}" id="${id}" onclick="chooseConnect('${id}', 'address')">${item}</div>`
        // console.log(dom)
        log_elem.appendChild(dom) // += lalala
    })
}

function handleSubmit() {
    const server = document.getElementById('pop-up-display-address').innerText
    const username = document.getElementById('username').value
    const password = document.getElementById('password').value

    const value = {
        "session": 'EECG1',
        "server": server,
        "username": username,
        "passwd": password,
        "save_key": false
    }

    console.log(value)

    send_msg('login', value)
}

function handle_sessions(value) {
    // TODO: integrated with GUI
    // window.open('./debugger.html')
    // printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)
    
    // console.log(value)
    const log_elem = document.getElementById("test")
    const dom = document.createElement("div")
    // const session_name = 'test'
    const a = `<div class="container">
    <div class="ui placeholder segment">
      <div class="ui two column very relaxed stackable grid">
        <div class="column">
          <div class="ui form">
            
            <div class="field">
              <label>Username</label>
              <div class="ui left icon input">
                <input type="text" placeholder="Username" id="username">
                <i class="user icon"></i>
              </div>
            </div>

            <div class="field">
              <label>Password</label>
              <div class="ui left icon input">
                <input type="password" placeholder="Password" id="password">
                <i class="lock icon"></i>
              </div>
            </div>

            <div class="field">
              <label>Choose a Server</label>
              <div class="ui selection dropdown" style="z-index: 99;">
                <input type="hidden" name="address">
                <i class="dropdown icon" onclick="chooseConnect('show', 'address')"></i>
                <div class="default text" id="pop-up-display-address">race</div>
                <div class="menu" id="pop-up-menu-address" style="display: none">
                </div>
              </div>
            </div>

            <div class="ui blue submit button" onclick="handleSubmit()">Login</div>
          </div>
        </div>

        <div class="column">
          <div class="ui form">

            <div class="field" style="height: 61px;">
              <label>Reset VNC</label>
              <div class="ui slider checkbox" style="margin-top: 12px; margin-bottom: 6px">
                <input type="checkbox" name="newsletter">
                <label>Reset the VNC</label>
              </div>
            </div>

            <div class="field">
              <label>New VNC Password</label>
              <div class="ui left icon input">
                <input type="text" placeholder="Type your new password">
                <i class="lock icon"></i>
              </div>
            </div>

          </div>
        </div>
      </div>
      <div class="ui vertical divider">
        UG Remote
      </div>
      </div>
    </div>`
    dom.innerHTML = a
    log_elem.appendChild(dom)
    handle_new_session(value)
    // printLog(`handle_sessions: ${JSON.stringify(value, null, ' ')}`)
    SESSIONS = value
}

function chooseConnect(type, selector) {
    const currentSelector = document.getElementById(`pop-up-menu-${selector}`);
    // console.log(type, currentSelector.style.display);
    if (type === 'show') {
      if (currentSelector.style.display === 'none') {
        currentSelector.style.display = 'block';
      } else {
        currentSelector.style.display = 'none'
      }
    } else {
      const target = document.getElementById(type);
      document.getElementById(`pop-up-display-${selector}`).innerHTML = target.innerHTML;
      currentSelector.style.display = 'none';
    }
  }

function handle_login_ack(value){
    alert("Login: " + value)
}

function handle_recv(value){
    TERM.write(atob(value["d"]))
}

function handle_terminal(value){
    // TODO: should add a parameter to allow reuse of this function for different terminals
    TERM.write(atob(value))
}

function handle_main(key, value) {
    if (key === "sessions") {
        handle_sessions(value)
    }
    else if (key === "login_ack"){
        handle_login_ack(value)
    }
    else if (key === "recv"){
        handle_recv(value)
    }
    else {
        printLog(`handle_main: Unknown key=${key}, value=${value}`)
        return false
    }

    return true
}

async function listen() {
    let running = true;
    while (running) {
        let recv_data = await IPC_RECV.receive()
        recv_data = recv_data.toString("utf-8")
        // printLog(recv_data)
        const recv_parsed = JSON.parse(recv_data)
        for (const key in recv_parsed) {
            if (!handle_main(key, recv_parsed[key])) {
                running = false
                break
            }
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    IPC_RECV.bind("tcp://*:8001").then(r => {
            printLog("Binding successful")

            const PyMotron = spawn(
                PYTHON_PATH,
                [
                    "-u",
                    PYMOTRON_PATH,
                    8000,
                    8001
                ],
                {
                    cwd: CWD_PATH
                });

            PyMotron.stdout.on("data", data => {
                // printLog(`\nPyMotron stdout:\n ---\n ${data}---`);
            });

            PyMotron.stderr.on("data", data => {
                printLog(`\nPyMotron stderr:\n ---\n ${data}---`);
            });

            PyMotron.on('error', (error) => {
                printLog(`\nPyMotron error: ${error.message}`);
            });

            PyMotron.on("close", code => {
                printLog(`\nPyMotron exited with code ${code}`);
            });

            IPC_SEND.connect("tcp://127.0.0.1:8000")

            send_msg("sync")

            listen().then()
        }
    )
})

function debug_submit() {
    const debug_key = document.getElementById("debug_key")
    const debug_value = document.getElementById("debug_value")

    const debug_value_JSON = (debug_value.value === "")?null:JSON.parse(debug_value.value)

    send_msg(debug_key.value, debug_value_JSON)

    return false
}



