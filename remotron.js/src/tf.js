const fs = require('fs')
const path = require('path')

const local_homedir = require('os').homedir()

function isDir(mode) {
    return (mode & fs.constants.S_IFMT) === fs.constants.S_IFDIR
}

// https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string/10420404
function humanFileSize(size_in_bytes) {
    const i = (size_in_bytes === 0) ? 0 : Math.floor(Math.log(size_in_bytes) / Math.log(1024))
    return (size_in_bytes / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
}


class TransferManager {
    session = null

    local_cwd = null
    remote_cwd = null

    local_checked_files = new Set()
    remote_checked_files = new Set()

    constructor(session_name) {
        this.session = session_name

        this.local_cwd = local_homedir
        this.remote_cwd = null

        this.local_checked_files = new Set()
        this.remote_checked_files = new Set()

        const tf_page = document.getElementById(`${session_name}-tf`)
        const tf_div = document.createElement("div")
        tf_page.appendChild(tf_div)
        tf_div.className = "ui grid"

        const tf_toolbar = document.createElement("div")
        tf_toolbar.className = "row"
        tf_toolbar.innerHTML = `
<div style="width: 300px; margin: auto" class="two ui buttons">
<button style="margin-right: 8px" id="${session_name}-tf-upload" class="ui right labeled icon green button">
  <i class="right arrow icon"></i>
  Upload
</button>
<button style="margin-left: 8px" id="${session_name}-tf-download" class="ui labeled icon blue button">
  <i class="left arrow icon"></i>
  Download
</button>
</div>

`
        tf_div.appendChild(tf_toolbar)


        const local_div = document.createElement("div")
        local_div.className = "eight wide column"
        local_div.innerHTML = this.fmGenerateDiv("local")
        local_div.style.overflow = "scroll"
        local_div.style.height = "100vh"
        tf_div.appendChild(local_div)

        const remote_div = document.createElement("div")
        remote_div.className = "eight wide column"
        remote_div.innerHTML = this.fmGenerateDiv("remote")
        remote_div.style.overflow = "scroll"
        remote_div.style.height = "100vh"
        tf_div.appendChild(remote_div)

        // setup the callbacks on the toolbar
        const tf_download_button = document.getElementById(`${session_name}-tf-download`)
        tf_download_button.onclick = () => {
            this.tfDownload()
        }
        const tf_upload_button = document.getElementById(`${session_name}-tf-upload`)
        tf_upload_button.onclick = () => {
            this.tfUpload()
        }

        // setup the callbacks on the local side
        const local_fm_addrbar_form = document.getElementById(`${session_name}-local-fm_addrbar_form`)
        local_fm_addrbar_form.onsubmit = () => {
            return this.localVisit()
        }
        const local_fm_up_button = document.getElementById(`${session_name}-local-fm_up_button`)
        local_fm_up_button.onclick = () => {
            this.localUp()
        }
        const local_fm_checkall_box = document.getElementById(`${session_name}-local-fm_checkall_box`)
        local_fm_checkall_box.onclick = () => {
            this.fmCheckAll("local")
        }

        // setup the callbacks on the remote side
        const remote_fm_addrbar_form = document.getElementById(`${session_name}-remote-fm_addrbar_form`)
        remote_fm_addrbar_form.onsubmit = () => {
            return this.remoteVisit()
        }
        const remote_fm_up_button = document.getElementById(`${session_name}-remote-fm_up_button`)
        remote_fm_up_button.onclick = () => {
            this.remoteUp()
        }
        const remote_fm_checkall_box = document.getElementById(`${session_name}-remote-fm_checkall_box`)
        remote_fm_checkall_box.onclick = () => {
            this.fmCheckAll("remote")
        }

        const local_files = this.localLs("")
        this.fmUpdateAddrBar("local")
        this.fmUpdateFileView("local", local_files)
    }

    fmGenerateDiv(side) {
        return `
<form class="ui action fluid input" id="${this.session}-${side}-fm_addrbar_form">
    <button class="ui blue icon button" id="${this.session}-${side}-fm_up_button" type="button">
        <i class="arrow up icon"></i>
    </button>
    <label for="${this.session}-${side}-fm_addrbar""></label><input id="${this.session}-${side}-fm_addrbar" type="text">
    <button class="ui teal right labeled icon button" type="submit">
        <i class="arrow right icon"></i>
        Go
    </button>
</form>
<table class="ui celled striped table">
    <thead>
    <tr>
        <th class="collapsing">
            <div class="ui fitted checkbox">
                <input id="${this.session}-${side}-fm_checkall_box" type="checkbox">
                <label for="${this.session}-${side}-fm_checkall_box"></label>
            </div>
        </th>

        <th>Name</th>
        <th style="width: 12ch">Size</th>
        <th class="collapsing">Date Accessed</th>
        <th class="collapsing">Date Modified</th>
    </tr>
    </thead>
    <tbody id="${this.session}-${side}-file_table_body">
    </tbody>
</table>
`
    }

    tfClose() {
        // TODO: check whether we do need this function
        // TODO: clean the DOM
        this.local_cwd = null
        this.remote_cwd = null
    }

    fmUpdateAddrBar(side) {
        this.fmUncheckCheckAll(side)
        if (side === "local") {
            this.local_checked_files = new Set()
        } else {
            this.remote_checked_files = new Set()
        }

        const fm_addrbar = document.getElementById(`${this.session}-${side}-fm_addrbar`)
        if (side === "local") {
            fm_addrbar.value = this.local_cwd
        } else {
            fm_addrbar.value = this.remote_cwd
        }
        const fm_addrbar_form = document.getElementById(`${this.session}-${side}-fm_addrbar_form`)
        fm_addrbar_form.classList.remove("error")
    }

    fmUpdateFileView(side, file_list) {
        const file_table_body = document.getElementById(`${this.session}-${side}-file_table_body`)
        file_table_body.innerHTML = ""

        file_list.forEach((file) => {
            const new_tr = document.createElement("tr")

            const checkbox_td = document.createElement("td")
            checkbox_td.className = "center aligned"

            const fm_checkbox_div = document.createElement("div")
            fm_checkbox_div.className = "ui fitted checkbox"
            const fm_checkbox = document.createElement("input")
            fm_checkbox.className = `${this.session}-${side}-fm_checkbox`
            fm_checkbox.type = "checkbox"
            fm_checkbox.setAttribute("filename", file["name"])
            fm_checkbox.onclick = () => {
                this.fmUncheckCheckAll(side)
                this.fmCheck(side, fm_checkbox)
            }
            fm_checkbox_div.appendChild(fm_checkbox)
            fm_checkbox_div.appendChild(document.createElement("label"))
            checkbox_td.appendChild(fm_checkbox_div)

            new_tr.appendChild(checkbox_td)

            const name_td = document.createElement("td")
            let size_td = document.createElement("td")
            if (isDir(file["mode"])) {
                name_td.innerHTML = "<i class=\"folder icon\"></i> "
                const enter_link = document.createElement("a")
                enter_link.style.userSelect = "none"
                enter_link.innerText = file["name"]
                if (side === "local") {
                    enter_link.onclick = () => {
                        const dest_files = this.localLs(path.resolve(this.local_cwd, file["name"]))
                        this.fmUpdateAddrBar(side)
                        this.fmUpdateFileView(side, dest_files)
                    }
                } else {
                    enter_link.onclick = () => {
                        this.remoteLs("./" + file["name"])
                    }
                }
                name_td.append(enter_link)
            } else {
                name_td.innerHTML = "<i class=\"file icon\"></i> "
                name_td.innerHTML += file["name"]
                size_td.innerHTML = humanFileSize(file["size"])
            }
            new_tr.appendChild(name_td)
            new_tr.appendChild(size_td)

            const atime_td = document.createElement("td")
            if (side === "local") {
                atime_td.innerHTML = file["atime"].toLocaleDateString()
            } else {
                // console.log(file["atime"])
                atime_td.innerHTML = new Date(file["atime"] * 1000).toLocaleDateString()
            }
            new_tr.appendChild(atime_td)

            const mtime_td = document.createElement("td")
            if (side === "local") {
                mtime_td.innerHTML = file["mtime"].toLocaleDateString()
            } else {
                mtime_td.innerHTML = new Date(file["mtime"] * 1000).toLocaleDateString()
            }
            new_tr.appendChild(mtime_td)

            file_table_body.appendChild(new_tr)
        })
    }

    fmCheck(side, fm_checkbox, check = null) {
        if (check === null) {
            check = fm_checkbox.checked
        }
        fm_checkbox.checked = check
        const filename = fm_checkbox.getAttribute("filename")
        const fm_checked_files = (side === "local") ? this.local_checked_files : this.remote_checked_files
        // const fm_cwd = (side === "local")?this.local_cwd : this.remote_cwd

        if (check) {
            fm_checked_files.add(filename)
        } else {
            fm_checked_files.delete(filename)
        }
    }

    fmCheckAll(side) {
        const fm_checkall_box = document.getElementById(`${this.session}-${side}-fm_checkall_box`)
        const fm_checkboxes = document.getElementsByClassName(`${this.session}-${side}-fm_checkbox`)

        if (fm_checkall_box.checked) {
            for (let fm_checkbox of fm_checkboxes) {
                this.fmCheck(side, fm_checkbox, true)
            }
        } else {
            for (let fm_checkbox of fm_checkboxes) {
                this.fmCheck(side, fm_checkbox, false)
            }
        }
    }

    fmUncheckCheckAll(side) {
        document.getElementById(`${this.session}-${side}-fm_checkall_box`).checked = false
    }

    localLs(path_input) {
        let new_cwd = this.local_cwd
        if (path_input !== "") {
            new_cwd = path.resolve(this.local_cwd, path_input)
        }

        const files = fs.readdirSync(new_cwd)
        let file_list = []
        files.forEach((filename) => {
            // TODO: should support showing hidden files
            if (filename.startsWith(".")) {
                return
            }
            const full_path = path.resolve(new_cwd, filename)
            try {
                const attrs = fs.statSync(full_path)
                file_list.push({
                    "name": filename,
                    "mode": attrs["mode"],
                    "size": attrs["size"],
                    "atime": attrs["atime"],
                    "mtime": attrs["mtime"]
                })
            } catch (e) {
                file_list.push({
                    "name": filename,
                    "mode": 0,
                    "size": 0,
                    "atime": new Date(0),
                    "mtime": new Date(0)
                })
            }
        })
        this.local_cwd = new_cwd
        return file_list
    }

    localUp() {
        try {
            const dest_files = this.localLs(path.resolve(this.local_cwd, ".."))
            this.fmUpdateAddrBar("local")
            this.fmUpdateFileView("local", dest_files)
        } catch (e) {
            alert(e)
        }
    }

    localVisit() {
        const fm_addrbar = document.getElementById(`${this.session}-local-fm_addrbar`)
        try {
            const dest_files = this.localLs(fm_addrbar.value)
            this.fmUpdateAddrBar("local")
            this.fmUpdateFileView("local", dest_files)
        } catch (e) {
            const fm_addrbar_form = document.getElementById(`${this.session}-local-fm_addrbar_form`)
            fm_addrbar_form.classList.add("error")
            alert(e)
        }

        return false
    }

    remoteLs(path_input) {
        send_msg("sftp_visit", {
            "session": this.session,
            "path": path_input
        })
    }

    remoteVisit() {
        const fm_addrbar = document.getElementById(`${this.session}-remote-fm_addrbar`)
        this.remoteLs(fm_addrbar.value)
        return false
    }

    remoteUp() {
        this.remoteLs("..")
    }

    tfUpload() {
        // TODO: check whether there is a file with the same name exisitng in the same directory
        //  to prevent overwriting existing files
        for (const file_name of this.local_checked_files) {
            send_msg("sftp_upload", {
                "session": this.session,
                "remote": path.resolve(this.remote_cwd, file_name),
                "local": path.resolve(this.local_cwd, file_name)
            })
        }
    }

    tfDownload() {
        // TODO: check whether there is a file with the same name exisitng in the same directory
        //  to prevent overwriting existing files
        for (const file_name of this.remote_checked_files) {
            send_msg("sftp_download", {
                "session": this.session,
                "remote": path.resolve(this.remote_cwd, file_name),
                "local": path.resolve(this.local_cwd, file_name)
            })
        }

    }
}

module.exports.TransferManager = TransferManager
