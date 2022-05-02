import React from 'react';

export default class AdComponent extends React.Component {
  componentDidMount() {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  }

  render() {
    return (
        <ins className={'adsbygoogle'}
             style={{
               display: 'block',
               width: '320px',
               height: '300px',
               marginLeft: 'auto',
               marginRight: 'auto',
               marginTop: '150px',
             }}
             {...this.props}
             data-ad-format={'auto'}
             data-full-width-responsive={'true'}/>
    );
  }
}