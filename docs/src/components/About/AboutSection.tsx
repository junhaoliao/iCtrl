import Link from "@docusaurus/Link";
import {
    Avatar,
    Divider,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Typography,
} from "@mui/material";

import {PersonInfo} from "./info";


interface AboutSectionProps {
    list: PersonInfo[];
    title: string;
}

/**
 * Renders an About section with a title and contributors.
 *
 * @param props
 * @param props.list
 * @param props.title
 * @return
 */
const AboutSection = ({list, title}: AboutSectionProps) => (
    <>
        <Divider sx={{borderColor: "var(--ifm-toc-border-color)"}}>
            <Typography variant={"subtitle1"}>
                {title}
            </Typography>
        </Divider>
        <List className={"selectable"}>
            {list.map((i) => (
                <ListItem key={i.name}>
                    {i.pic && <ListItemAvatar>
                        <Avatar
                            src={i.pic}
                            sx={{filter: "brightness(105%)", width: 48, height: 48}}/>
                              </ListItemAvatar>}
                    <ListItemText
                        primary={i.name}
                        secondary={
                            <div>
                                {i.desc && <div>
                                    {i.desc}
                                           </div>}
                                <Link to={i.url}>
                                    {i.url}
                                </Link>
                            </div>
                        }
                        slotProps={{
                            secondary: {
                                component: "div",
                                fontSize: "0.8rem",
                                color: "var(--ifm-font-color-secondary)",
                            },
                        }}/>
                </ListItem>
            ))}
        </List>
    </>
);

export default AboutSection;
