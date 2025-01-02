import React from "react";


interface PersonInfo {
    name: string;
    url: string;
    desc: React.ReactElement | string;
    pic?: string;
}

const SUPERVISORS: PersonInfo[] = [
    {
        name: "Timorabadi, Hamid",
        url: "https://www.ece.utoronto.ca/people/timorabadi-h/",
        desc: `University of Toronto Electrical & Computer Engineering capstone project
        supervisor.`,
    },
];

const SPECIAL_THANKS: PersonInfo[] = [
    {
        name: "Betz, Vaughn",
        url: "https://www.eecg.utoronto.ca/~vaughn/",
        desc: `Extensive support for the application's integration into course
    "ECE297 - Software Design & Communication" at University of Toronto.`,
    },
    {
        name: "Phang, Khoman",
        url: "https://www.eecg.utoronto.ca/~kphang/",
        desc: `University of Toronto Electrical & Computer Engineering capstone project
        administrator.`,
    },
    {
        name: "Richard Junjie Shen",
        url: "https://www.linkedin.com/in/junjie-shen-38a450210/",
        desc: "Icon designer.",
    },
];

const CONTRIBUTORS: PersonInfo[] = [
    {
        name: "Junhao Liao",
        url: "https://junhao.ca",
        pic: "/img/about/junhao-pic.webp",
        desc:
    <>
        <div>Software Developer @ YScope</div>
        <div>University of Toronto - ECE 2T1 + PEY</div>
    </>,
    },
    {
        name: "Yizhong Xu",
        url: "https://www.linkedin.com/in/yizhong-xu-076bb9157/",
        pic: "/img/about/yizhong-pic.webp",
        desc:
    <>
        <div>Software Developer @ CNOOC</div>
        <div>University of Toronto - ECE 2T1 + PEY</div>
    </>,
    },
    {
        name: "Haoran Zhang",
        url: "https://www.linkedin.com/in/haoran-zhang-424b33196/",
        pic: "/img/about/haoran-pic.webp",
        desc:
    <>
        <div>Software Engineer @ Baidu</div>
        <div>University of Toronto - ECE 2T1 + PEY</div>
    </>,
    },
    {
        name: "Jiaxing Li",
        url: "https://www.linkedin.com/in/jiaxing-leo-li/",
        pic: "/img/about/jiaxing-pic.webp",
        desc:
    <>
        <div>Software Engineer @ Intel</div>
        <div>University of Toronto - ECE 2T1 + PEY</div>
    </>,
    },
    {
        name: "Leo HC Li",
        url: "https://me.leo6leo.cool",
        pic: "/img/about/leo-pic.webp",
        desc: "University of Toronto - ECE 2T4 + PEY",
    },
];

export type {PersonInfo};
export {
    CONTRIBUTORS,
    SPECIAL_THANKS,
    SUPERVISORS,
};
