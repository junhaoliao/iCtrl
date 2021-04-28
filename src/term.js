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
    }

    fit() {
        if (this.terminal_div.getBoundingClientRect().width !== 0) {
            this.terminal_div.style.height = `${document.body.clientHeight - 40}px`
            this.fitAddon.fit();
        }
    }
}

module.exports.Term = Term