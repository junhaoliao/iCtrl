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

import {themes as prismThemes} from "prism-react-renderer";

import type * as Preset from "@docusaurus/preset-classic";
import type {Config} from "@docusaurus/types";


const config: Config = {
    favicon: "img/favicon.png",
    tagline: "A Simple VNC + SSH Console + SFTP Client",
    title: "iCtrl",

    baseUrl: "/",
    url: "https://ictrl.ca",

    organizationName: "junhaoliao",
    projectName: "iCtrl",

    onBrokenLinks: "throw",
    onBrokenMarkdownLinks: "warn",

    i18n: {
        defaultLocale: "en",
        locales: [
            "en",
            "zh",
        ],
    },

    presets: [
        [
            "classic",
            {
                blog: false,

                // docs: {
                //     editUrl:
                //         "https://github.com/junhaoliao/iCtrl/tree/main/docs/docs",
                //     sidebarPath: "./sidebars.ts",
                // },
                docs: false,
                theme: {
                    customCss: "./src/css/custom.css",
                },
            } satisfies Preset.Options,
        ],
    ],

    themeConfig: {
        colorMode: {
            respectPrefersColorScheme: true,
        },

        image: "img/ictrl-social-card.png",
        navbar: {
            title: "iCtrl",
            logo: {
                alt: "iCtrl Logo",
                src: "img/logo.svg",
            },
            items: [
                // {
                //     type: "docSidebar",
                //     sidebarId: "devDocsSidebar",
                //     label: "Docs",
                // },
                {
                    to: "/about",
                    label: "About",
                },
                {
                    type: "localeDropdown",
                    position: "right",
                },
                {
                    type: "custom-ReactGitHubButton",
                    position: "right",
                },
            ],
        },

        footer: {
            style: "dark",
            copyright: `Copyright © 2019-${new Date().getFullYear()} iCtrl Developers.`,
        },

        prism: {
            theme: prismThemes.github,
            darkTheme: prismThemes.dracula,
        },
    } satisfies Preset.ThemeConfig,
};

export default config;
