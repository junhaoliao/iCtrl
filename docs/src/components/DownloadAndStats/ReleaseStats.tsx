import {translate} from "@docusaurus/Translate";
import {
    Tooltip,
    Typography,
} from "@mui/material";
import {ReleaseInfo} from "@site/src/components/DownloadAndStats/index";


/**
 * Converts a provided Date object into a locale-sensitive string representation.
 *
 * @param date
 * @return A string representation of the provided Date object in the default locale, including its
 * long time zone name.
 */
const getLocaleString = (date: Date) => {
    // eslint-disable-next-line no-undefined
    return date.toLocaleString(undefined, {timeZoneName: "long"});
};

interface ReleaseStatsProps {
        latestReleaseInfo: ReleaseInfo,
    latestReleaseDownloadCount: number,
    historicalDownloadCount: number | null
}

/**
 * Renders the latest release's download counts on all platforms and the historical download
 * counts of all versions.
 *
 * @param props
 * @param props.latestReleaseInfo
 * @param props.latestReleaseDownloadCount
 * @param props.historicalDownloadCount
 * @return
 */
const ReleaseStats = ({
    latestReleaseInfo,
    latestReleaseDownloadCount,
    historicalDownloadCount,
}: ReleaseStatsProps) => (
    <Typography
        marginTop={"10px"}
        variant={"subtitle1"}
    >
        <Tooltip title={getLocaleString(latestReleaseInfo.publishDate)}>
            <b style={{textDecoration: "underline"}}>
                {latestReleaseInfo.name}
            </b>
        </Tooltip>
        {` ${
            translate({message: "downloads", id: "stats.latestReleaseDownloadCount"})
        }: ${latestReleaseDownloadCount}`}
        {historicalDownloadCount &&
            ` | ${
                translate({message: "Historical downloads", id: "stats.historicalDownloadCount"})
            }: ${historicalDownloadCount}`}
    </Typography>
);


export default ReleaseStats;
