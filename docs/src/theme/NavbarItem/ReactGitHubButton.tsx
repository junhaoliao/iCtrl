import GitHubButton from "react-github-btn";


/**
 * Renders a GitHub button that displays stars and hyperlinks to the iCtrl repo.
 *
 * @return
 */
const ReactGitHubButton = () => (
    <div style={{marginTop: "10px", marginRight: "9px", marginLeft: "3px"}}>
        <GitHubButton
            aria-label={"Star junhaoliao/iCtrl on GitHub"}
            data-show-count={"true"}
            data-size={"large"}
            href={"https://github.com/junhaoliao/iCtrl"}
            data-color-scheme={"no-preference: light_high_contrast; light: light_high_contrast;" +
                "dark: light_high_contrast;"}
        >
            Star
        </GitHubButton>
    </div>
);

export default ReactGitHubButton;
