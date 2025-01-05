/*
 * Copyright (c) 2025 iCtrl Developers
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to
 *  deal in the Software without restriction, including without limitation the
 *  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 *  sell copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 *  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 *  IN THE SOFTWARE.
 */

import Translate from "@docusaurus/Translate";
import {
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
} from "@mui/material";
import ReactGitHubButton from "@site/src/theme/NavbarItem/ReactGitHubButton";


interface PostDownloadDialogProps {
    isOpen: boolean;

    onClose: () => void;
}

/**
 * Renders a dialog box displayed after a successful download action.
 *
 * @param props
 * @param props.isOpen
 * @param props.onClose
 * @return
 */
const PostDownloadDialog = ({isOpen, onClose}: PostDownloadDialogProps) => (
    <Dialog
        aria-describedby={"post-download-dialog-description"}
        aria-labelledby={"post-download-dialog-title"}
        keepMounted={true}
        open={isOpen}
        onClose={onClose}
    >
        <DialogTitle>
            <Translate id={"postDownloadDialog.title"}>
                Thank you for downloading iCtrl!
            </Translate>
        </DialogTitle>
        <DialogContent>
            <DialogContentText>
                <Translate id={"postDownloadDialog.description1"}>
                    iCtrl is a free open-source project.
                </Translate>
                <br/>
                <Translate id={"postDownloadDialog.description2"}>
                    It will be great if you can support us with just a few clicks.
                </Translate>
            </DialogContentText>
        </DialogContent>
        <DialogActions>
            <ReactGitHubButton/>
        </DialogActions>
    </Dialog>
);


export default PostDownloadDialog;
