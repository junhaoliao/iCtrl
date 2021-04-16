function printLog(text) {
    const log_elem = document.getElementById("logs")
    const now = new Date()
    text = now.getHours() + ":" + now.getMinutes() + ":" + now.getSeconds() + ": " + text + "\n"

    if (log_elem){
        const new_log = document.createElement("p")
        log_elem.appendChild(new_log)
        new_log.innerText = text
    } else{
        alert(text)
    }
}