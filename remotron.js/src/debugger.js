const log_elem = document.getElementById("logs")

function printLog(text) {
    const now = new Date()
    text = now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds() + ": " + text + "\n"

    if (log_elem) {
        const new_log = document.createElement("p")
        log_elem.appendChild(new_log)
        new_log.innerText = text
    } else {
        console.log(text)
    }
}

function debug_submit() {
    const debug_key = document.getElementById("debug_key").value
    const debug_value = document.getElementById("debug_value").value

    const debug_value_JSON = (debug_value === "") ? null : JSON.parse(debug_value)

    send_msg(debug_key, debug_value_JSON)

    return false
}

PyMotron.stdout.on("data", data => {
    printLog(`\nPyMotron stdout:\n${data}`);
});

PyMotron.stderr.on("data", data => {
    printLog(`\nPyMotron stderr:\n${data}`);
});

PyMotron.on('error', (error) => {
    printLog(`\nPyMotron error: ${error.message}`);
});

PyMotron.on("close", code => {
    printLog(`\nPyMotron exited with code ${code}`);
});
