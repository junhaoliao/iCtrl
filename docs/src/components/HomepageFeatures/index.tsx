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

import React from "react";

import {clsx} from "clsx";

import Translate, {translate} from "@docusaurus/Translate";
import IntuitiveAndAccessibleSvg from "@site/static/img/intuitive-and-accessible.svg";
import SecureAndVersatileSvg from "@site/static/img/secure-and-versatile.svg";
import SmartAndAdaptiveSvg from "@site/static/img/smart-and-adaptive.svg";
import Heading from "@theme/Heading";

import styles from "./styles.module.css";


type FeatureProps = {
    title: string;
    Svg: React.ComponentType<React.ComponentProps<"svg">>;
    description: React.ReactElement;
};

const FeatureList: FeatureProps[] = [
    {
        title: translate({
            message: "Intuitive and Accessible",
            id: "features.intuitiveAndAccessible.title",
        }),
        Svg: IntuitiveAndAccessibleSvg,
        description: (
            <Translate id={"features.intuitiveAndAccessible.description"}>
                Effortless remote access via desktop app, browser, or even on mobile devices.
            </Translate>
        ),
    },
    {
        title: translate({
            message: "Secure and Versatile",
            id: "features.secureAndVersatile.title",
        }),
        Svg: SecureAndVersatileSvg,
        description: (
            <Translate id={"features.secureAndVersatile.description"}>
                Secure connections with SSH, SFTP, and graphical VNC, all in one.
            </Translate>
        ),
    },
    {
        title: translate({
            message: "Smart and Adaptive",
            id: "features.smartAndAdaptive.title",
        }),
        Svg: SmartAndAdaptiveSvg,
        description: (
            <Translate id={"features.smartAndAdaptive.description"}>
                Workload detection and machine switching for maximum productivity.
            </Translate>
        ),
    },
];

/**
 * Renders a single feature.
 *
 * @param props
 * @param props.title
 * @param props.Svg
 * @param props.description
 * @return
 */
const Feature = ({title, Svg, description}: FeatureProps) => (
    <div className={clsx("col col--4")}>
        <div className={"text--center"}>
            <Svg
                className={styles.featureSvg}
                role={"img"}/>
        </div>
        <div className={"text--center padding-horiz--md"}>
            <Heading as={"h3"}>
                {title}
            </Heading>
            <p>
                {description}
            </p>
        </div>
    </div>
);

/**
 * Renders a section of features on the homepage.
 *
 * @return
 */
const HomepageFeatures = () => (
    <section className={styles.features}>
        <div className={"container"}>
            <div className={"row"}>
                {FeatureList.map((props, idx) => (
                    <Feature
                        key={idx}
                        {...props}/>
                ))}
            </div>
        </div>
    </section>
);

export default HomepageFeatures;
