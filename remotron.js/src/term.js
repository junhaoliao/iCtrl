const {Terminal} = require("xterm");
const { FitAddon } = require ("xterm-addon-fit")
class Term{
    terminal = null
    constructor(session_name) {
        this.terminal = new Terminal()
        this.terminal.open(document.getElementById(`${session_name}-terminal`))
        this.terminal.onKey(async (e) => {
            send_msg("send", {
                "s": session_name,
                "d": e.key
            })
        });
        const fitAddon = new FitAddon();
        this.terminal.loadAddon(fitAddon);

        this.terminal.onResize((e)=>{
            console.log(e)
            send_msg("resize", {
                "s": session_name,
                "c": e.cols,
                "r": e.rows
            })
        })
        // TODO: put the fit addons in a global array and use a single event listener
        window.addEventListener('resize', ()=>{
            fitAddon.fit();
        });
    }
}
module.exports.Term = Term