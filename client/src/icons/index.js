import {SvgIcon} from '@material-ui/core';
import React from 'react';

export const ShortcutIcon = (props) => {
  return (
    <SvgIcon {...props}>
      <path d="M21,11l-6-6v5H8c-2.76,0-5,2.24-5,5v4h2v-4c0-1.65,1.35-3,3-3h7v5L21,11z"/>
    </SvgIcon>
  );
}

export const DensityIcon = (props) => {
  return (
    <SvgIcon {...props}>
        <path d="M21,8H3V4h18V8z M21,10H3v4h18V10z M21,16H3v4h18V16z"/>
    </SvgIcon>
  );
}

export const DensityCompactIcon = (props) => {
  return (
    <SvgIcon {...props}>
        <path d="M4 15h16v-2H4v2zm0 4h16v-2H4v2zm0-8h16V9H4v2zm0-6v2h16V5H4z"/>
    </SvgIcon>
  );
}

export const DensityStandardIcon = (props) => {
  return (
    <SvgIcon {...props}>
        <path d="M21,8H3V4h18V8z M21,10H3v4h18V10z M21,16H3v4h18V16z"/>
    </SvgIcon>
  );
}


export const DensityComfortableIcon = (props) => {
  return (
    <SvgIcon {...props}>
        <path d="M4 18h17v-6H4v6zM4 5v6h17V5H4z"/>
    </SvgIcon>
  );
}


