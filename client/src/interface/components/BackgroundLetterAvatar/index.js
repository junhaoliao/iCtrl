/*
 * Copyright (c) 2021-2022 iCtrl Developers
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

// Reference: https://next.material-ui.com/components/avatars/
import React, {createRef} from 'react';
import Avatar from '@mui/material/Avatar';
import {Badge} from '@mui/material';

// Reference: https://24ways.org/2010/calculating-color-contrast
const getContrastYIQ = hexcolor => {
  const r = parseInt(hexcolor.substr(1, 2), 16);
  const g = parseInt(hexcolor.substr(3, 2), 16);
  const b = parseInt(hexcolor.substr(5, 2), 16);
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (yiq >= 160) ? 'dimgrey' : 'white';
};

function stringToColor(string) {
  let hash = 0;
  let i;

  for (i = 0; i < string.length; i += 1) {
    hash = string.charCodeAt(i) + ((hash << 5) - hash);
  }

  let color = '#';

  for (i = 0; i < 3; i += 1) {
    const value = (hash >> (i * 8)) & 0xff;
    color += `00${value.toString(16)}`.substr(-2);
  }

  return color;
}

class BackgroundLetterAvatar extends React.Component {
  constructor(props) {
    super(props);

    this.wrapperRef = createRef();
    this.nameRef = createRef();

    this.state = {
      fontSize: 12,
    };
  }

  setFontSize = () => {
    if (this.nameRef.current.offsetWidth + 5 <
        this.wrapperRef.current.offsetWidth - 5) {
      if (this.nameRef.current.offsetWidth === 0) {
        return;
      }
      this.setState({
        fontSize: this.state.fontSize + 1,
      });
      setTimeout(this.setFontSize, 0);
    } else if (this.nameRef.current.offsetWidth - 5 >
        this.wrapperRef.current.offsetWidth - 5) {
      this.setState({
        fontSize: this.state.fontSize - 1,
      });
      setTimeout(this.setFontSize, 0);
    }
  };

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (prevProps.name !== this.props.name) {
      this.setFontSize();
    }
  }

  componentDidMount() {
    this.setFontSize();
  }

  render() {
    const {name, badgeContent} = this.props;
    const {fontSize} = this.state;
    const backgroundColor = stringToColor(name);

    return (<Badge
        ref={this.wrapperRef}
        overlap="circular"
        anchorOrigin={{vertical: 'bottom', horizontal: 'right'}}
        badgeContent={badgeContent}
    >
      <Avatar
          sx={{
            backgroundColor: backgroundColor,
            fontSize: fontSize,
            whiteSpace: 'nowrap',
          }}>
                <span ref={this.nameRef}
                      style={{color: getContrastYIQ(backgroundColor)}}
                >
                    {name}
                </span>
      </Avatar>
    </Badge>);
  }
}

export default BackgroundLetterAvatar;