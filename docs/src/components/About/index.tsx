import {Grid2 as Grid} from "@mui/material";

import AboutSection from "./AboutSection";
import {
    CONTRIBUTORS,
    SPECIAL_THANKS,
    SUPERVISORS,
} from "./info";


/**
 * Renders an About element.
 *
 * @return
 */
const About = () => (
    <Grid
        columns={2}
        container={true}
        spacing={1}
    >
        <Grid size={{xs: 2, md: 1}}>
            <AboutSection
                list={SUPERVISORS}
                title={"Supervisor"}/>
            <AboutSection
                list={CONTRIBUTORS}
                title={"Core Contributors"}/>
        </Grid>
        <Grid size={{xs: 2, md: 1}}>
            <AboutSection
                list={SPECIAL_THANKS}
                title={"Special Thanks"}/>
        </Grid>
    </Grid>
);

export default About;
