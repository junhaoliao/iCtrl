import React from "react";

import { Input } from '@material-ui/core';

export default class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            counter: 1
        }
    }

    componentDidMount() {
        setInterval(()=>{
            this.setState({counter: this.state.counter + 1})
        }, 100);
    }

    render() {
        return(<div>
            <h1>Counter: </h1>
            <Input value={this.state.counter}/>
        </div>);
    }
}


