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

import {clsx} from "clsx";

import Translate from "@docusaurus/Translate";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import DownloadAndStats from "@site/src/components/DownloadAndStats";
import HomepageFeatures from "@site/src/components/HomepageFeatures";
import Heading from "@theme/Heading";
import Layout from "@theme/Layout";

import styles from "./index.module.css";


/**
 * Renders a home page header.
 *
 * @return
 */
const HomepageHeader = () => {
    const {siteConfig} = useDocusaurusContext();
    return (
        <header className={clsx("hero hero--primary", styles.heroBanner)}>
            <div className={"container"}>
                <Heading
                    as={"h1"}
                    className={"hero__title"}
                >
                    {siteConfig.title}
                </Heading>
                <p className={"hero__subtitle"}>
                    <Translate
                        id={"siteConfig.tagline"}
                        values={{tagline: siteConfig.tagline}}
                    >
                        {"{tagline}"}
                    </Translate>
                </p>
                <DownloadAndStats/>
            </div>
        </header>
    );
};

/**
 * Renders a layout for the homepage.
 *
 * @return
 */
const Home = () => {
    return (
        <Layout
            description={"iCtrl - A Simple VNC + SSH Console + SFTP Client"}
        >
            <HomepageHeader/>
            <main>
                <HomepageFeatures/>
            </main>
        </Layout>
    );
};

export default Home;
