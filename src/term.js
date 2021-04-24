const {Terminal} = require("xterm");
const {FitAddon} = require("xterm-addon-fit")

class Term {
    terminal = null
    terminal_div = null

    constructor(session_name) {
        this.terminal_div = document.getElementById(`${session_name}-terminal`)
        this.terminal = new Terminal()
        this.terminal.open(this.terminal_div)
        this.terminal.onKey(async (e) => {
            send_msg("send", {
                "s": session_name,
                "d": e.key
            })
        });
        const fitAddon = new FitAddon();
        this.terminal.loadAddon(fitAddon);

        this.terminal.onResize((e) => {
            console.log(e)
            send_msg("resize", {
                "s": session_name,
                "c": e.cols,
                "r": e.rows
            })
        })

        window.addEventListener('resize', () => {
            if (this.terminal_div.getBoundingClientRect().width !== 0) {
                // if the terminal div is not shown in the interface, don't resize
                fitAddon.fit();
            }
        });
    }
}

module.exports.Term = Term