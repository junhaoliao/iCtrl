const {Terminal} = require("xterm");
const {FitAddon} = require("xterm-addon-fit")

class Term {
    activated = false
    fitted = false
    fitAddon = null
    terminal = null
    terminal_div = null

    constructor(session_name) {
        this.terminal_div = document.getElementById(`${session_name}-terminal`)
        this.terminal = new Terminal()
        this.terminal.open(this.terminal_div)
        this.fitAddon = new FitAddon();
        this.terminal.loadAddon(this.fitAddon);

        this.terminal_div.onauxclick = (e)=>{
            if (e.which === 3){
                const selected_text = this.terminal.getSelection()
                navigator.clipboard.readText().then((pasteboard_text)=>{
                    if (selected_text === "" || selected_text === pasteboard_text){
                        this.terminal.clearSelection()
                        console.log("paste")
                        send_msg("send", {
                                "s": session_name,
                                "d": pasteboard_text
                        })
                    } else {
                        console.log("copy")
                        document.execCommand("copy")
                    }
                })
            }
        }
        this.terminal.onResize((e) => {
            send_msg("resize", {
                "s": session_name,
                "c": e.cols,
                "r": e.rows
            })
        })

        window.addEventListener('resize', () => {
            // if the terminal div is not shown in the interface, don't resize
            this.fit()
        });

        this.terminal.onKey(async (e) => {
            send_msg("send", {
                "s": session_name,
                "d": e.key
            })
        });

        this.terminal.attachCustomKeyEventHandler((e)=>{
            if (e.metaKey){
                if (e.key === "c"){
                    console.log("term: copy")
                    return false
                }
                else if (e.key === "v"){
                    console.log("term: paste")
                    navigator.clipboard.readText().then((text)=>{
                        send_msg("send", {
                            "s": session_name,
                            "d": text
                        })
                    })
                    return false
                }
            }
            return true
        })

        // this.terminal.viewport.onWheel = (e)=>{
        //     console.log(e)
        // }
    }

    fit() {
        if (this.terminal_div.getBoundingClientRect().width !== 0) {
            this.terminal_div.style.height = `${document.body.clientHeight - 40}px`
            this.fitAddon.fit();
        }
    }
}

module.exports.Term = Term