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
