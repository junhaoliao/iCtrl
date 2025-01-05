import React, {
    useEffect,
    useMemo,
    useState,
} from "react";

import axios from "axios";
import {UAParser} from "ua-parser-js";

import {translate} from "@docusaurus/Translate";
import {
    Paper,
    ToggleButton,
    ToggleButtonGroup,
    Tooltip,
} from "@mui/material";
import PostDownloadDialog from "@site/src/components/DownloadAndStats/PostDownloadDialog";
import ReleaseStats from "@site/src/components/DownloadAndStats/ReleaseStats";
import {Nullable} from "@site/src/typings/common";


enum PLATFORM {
    WINDOWS = "windows",
    MAC_INTEL = "mac-intel",
    MAC_ARM = "mac-arm",
}

const PLATFORMS: PLATFORM[] = Object.values(PLATFORM);

const PLATFORM_TO_DISPLAY_NAME: Record<PLATFORM, string> = {
    [PLATFORM.WINDOWS]: "Windows",
    [PLATFORM.MAC_INTEL]: "macOS (Intel)",
    [PLATFORM.MAC_ARM]: "macOS (ARM)",
};

const PLATFORM_TO_BINARY_NAME: Record<PLATFORM, string> = {
    [PLATFORM.WINDOWS]: "ictrl-desktop-setup.exe",
    [PLATFORM.MAC_INTEL]: "ictrl-desktop-darwin-x64.dmg",
    [PLATFORM.MAC_ARM]: "ictrl-desktop-darwin-arm64.dmg",
};

interface ReleaseInfo {
    downloadCount: Record<PLATFORM, number>;
    name: string;
    publishDate: Date;
}

/**
 * Fetches information about the latest release of a GitHub repository.
 *
 * @return An object containing the latest release information.
 */
const getLatestReleaseInfo = async (): Promise<ReleaseInfo> => {
    const {data} = await axios.get<{
        assets: Array<{ name: string, download_count: number }>;
        name: string;
        published_at: string;
    }>("https://api.github.com/repos/junhaoliao/iCtrl/releases/latest");

    const {assets, name: releaseName, published_at: publishedAt} = data;

    const counts: Record<PLATFORM, number> = {
        [PLATFORM.WINDOWS]: 0,
        [PLATFORM.MAC_INTEL]: 0,
        [PLATFORM.MAC_ARM]: 0,
    };

    for (const {name, download_count: downloadCount} of assets) {
        if (name.includes("exe") || name.includes("nupkg")) {
            counts[PLATFORM.WINDOWS] += downloadCount;
        } else if (name.includes("x64")) {
            counts[PLATFORM.MAC_INTEL] += downloadCount;
        } else if (name.includes("arm64")) {
            counts[PLATFORM.MAC_ARM] += downloadCount;
        }
    }

    return {
        downloadCount: counts,
        name: releaseName,
        publishDate: new Date(publishedAt),
    };
};

/**
 * Fetches all releases and sums up download counts on all platforms.
 *
 * @return The total historial download count.
 */
const getHistoricalDownloadCount = async (): Promise<number> => {
    const {data} = await axios.get<
        Array<{
            assets: Array<{ name: string, download_count: number }>;
        }>
    >("https://api.github.com/repos/junhaoliao/iCtrl/releases");

    let totalDownloadCount = 0;
    for (const release of data) {
        for (const asset of release.assets) {
            // exclude those named "RELEASE" because the file
            //  is used for Windows auto-update
            if ("RELEASES" !== asset.name) {
                totalDownloadCount += asset.download_count;
            }
        }
    }

    return totalDownloadCount;
};

/**
 * Detects the platform on which the application is running.
 *
 * @return The detected platform as a value from the PLATFORM
 * enumeration or null if the platform cannot be identified.
 */
const detectPlatform = (): Nullable<PLATFORM> => {
    const uap: UAParser = new UAParser();
    const {name} = uap.getOS();

    if ("undefined" === typeof name) {
        return null;
    }

    let platform: Nullable<PLATFORM> = null;
    switch (name) {
        case "Windows":
            platform = PLATFORM.WINDOWS;
            break;
        case "macOS": {
            // is mac, check whether is ARM by checking whether GPU vendor is Apple
            const canvas = document.createElement("canvas");
            const gl = canvas.getContext("webgl");
            const debuggerInfo = gl && gl.getExtension("WEBGL_debug_renderer_info");
            const renderer = debuggerInfo &&
                    gl.getParameter(debuggerInfo.UNMASKED_RENDERER_WEBGL) as string;

            if (renderer && renderer.match(/Apple/)) {
                if (!renderer.match(/Apple GPU/)) {
                    // must be ARM
                    platform = PLATFORM.MAC_ARM;
                } else {
                    // cannot really tell whether it is ARM-based
                    // because Safari tries to hide any platform-related info as of today
                    console.log("Unable to get processor type in Safari");
                }
            } else {
                platform = PLATFORM.MAC_INTEL;
            }
            break;
        }
        default:
            console.log(`Unknown platform: ${name}`);
            break;
    }

    return platform;
};


/**
 * Renders platform-specific download buttons while displaying relevant download statistics.
 *
 * @return
 */
const DownloadAndStats = () => {
    const [latestReleaseInfo, setLatestReleaseInfo] = useState<Nullable<ReleaseInfo>>(null);
    const [detectedPlatform, setDetectedPlatform] = useState<Nullable<PLATFORM>>(null);
    const [historicalDownloadCount, setHistoricalDownloadCount] = useState<Nullable<number>>(null);

    const [isPostDownloadDialogOpen, setIsPostDownloadDialogOpen] = useState<boolean>(false);

    const latestReleaseDownloadCount = useMemo(
        () => Object.values(latestReleaseInfo?.downloadCount ?? {})
            .reduce((acc, cur) => acc + cur, 0),
        [latestReleaseInfo]
    );

    const handlePlatformDownloadClick = (ev: React.MouseEvent<HTMLElement>) => {
        const {platform} = ev.currentTarget.dataset;
        if ("undefined" === typeof platform) {
            throw new Error("Invalid platform set on button");
        }

        const downloadLink = `https://github.com/junhaoliao/iCtrl/releases/latest/download/${
            PLATFORM_TO_BINARY_NAME[platform as PLATFORM]}`;

        window.open(downloadLink, "_self");

        setIsPostDownloadDialogOpen(true);
    };

    const handlePostDownloadDialogClose = () => {
        setIsPostDownloadDialogOpen(false);
    };

    useEffect(() => {
        setDetectedPlatform(detectPlatform());
    }, []);

    useEffect(() => {
        if (null !== latestReleaseInfo) {
            return;
        }

        getLatestReleaseInfo()
            .then((info) => {
                setLatestReleaseInfo(info);
            })
            .catch((e: unknown) => {
                console.error(e);
            });
    }, [latestReleaseInfo]);

    useEffect(() => {
        if (null !== historicalDownloadCount) {
            return;
        }
        getHistoricalDownloadCount()
            .then((count) => {
                setHistoricalDownloadCount(count);
            })
            .catch((e: unknown) => {
                console.error(e);
            });
    }, [historicalDownloadCount]);

    return (
        <>
            <div style={{display: "flex", justifyContent: "center"}}>
                <Paper>
                    <ToggleButtonGroup
                        color={"primary"}
                        exclusive={true}
                        value={detectedPlatform}
                    >
                        {PLATFORMS.map((platform) => (
                            <Tooltip
                                key={platform}
                                title={latestReleaseInfo ?
                                    `${latestReleaseInfo.downloadCount[platform]} ${translate({
                                        message: "downloads",
                                        id: "stats.platformReleaseDownloadCount",
                                    })}` :
                                    null}
                            >
                                <ToggleButton
                                    data-platform={platform}
                                    value={platform}
                                    onClick={handlePlatformDownloadClick}
                                >
                                    {PLATFORM_TO_DISPLAY_NAME[platform]}
                                </ToggleButton>
                            </Tooltip>
                        ))}
                    </ToggleButtonGroup>
                </Paper>
            </div>

            <br/>
            {latestReleaseInfo &&
                <ReleaseStats
                    historicalDownloadCount={historicalDownloadCount}
                    latestReleaseDownloadCount={latestReleaseDownloadCount}
                    latestReleaseInfo={latestReleaseInfo}/>}

            <PostDownloadDialog
                isOpen={isPostDownloadDialogOpen}
                onClose={handlePostDownloadDialogClose}/>
        </>
    );
};

export type {ReleaseInfo};
export default DownloadAndStats;
