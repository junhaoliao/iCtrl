import {SvgIcon} from '@mui/material';
import React from 'react';

export const ShortcutIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path
            d="M21,11l-6-6v5H8c-2.76,0-5,2.24-5,5v4h2v-4c0-1.65,1.35-3,3-3h7v5L21,11z"/>
      </SvgIcon>
  );
};

export const DensityIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path d="M21,8H3V4h18V8z M21,10H3v4h18V10z M21,16H3v4h18V16z"/>
      </SvgIcon>
  );
};

export const DensityCompactIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path d="M4 15h16v-2H4v2zm0 4h16v-2H4v2zm0-8h16V9H4v2zm0-6v2h16V5H4z"/>
      </SvgIcon>
  );
};

export const DensityStandardIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path d="M21,8H3V4h18V8z M21,10H3v4h18V10z M21,16H3v4h18V16z"/>
      </SvgIcon>
  );
};

export const DensityComfortableIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path d="M4 18h17v-6H4v6zM4 5v6h17V5H4z"/>
      </SvgIcon>
  );
};

// Reference: https://materialdesignicons.com/api/download/icon/svg/DCD0A183-A5DC-43BD-BC48-8FFF0CA0FA9C
export const ConsoleIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path
            d="M20,19V7H4V19H20M20,3A2,2 0 0,1 22,5V19A2,2 0 0,1 20,21H4A2,2 0 0,1 2,19V5C2,3.89 2.9,3 4,3H20M13,17V15H18V17H13M9.58,13L5.57,9H8.4L11.7,12.3C12.09,12.69 12.09,13.33 11.7,13.72L8.42,17H5.59L9.58,13Z"/>
      </SvgIcon>
  );
};

// Reference: https://materialdesignicons.com/api/download/icon/svg/A237199B-0B22-475F-93D1-DB45FA4D3205
export const RemoteDesktopIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path
            d="M3,2A2,2 0 0,0 1,4V16C1,17.11 1.9,18 3,18H10V20H8V22H16V20H14V18H21A2,2 0 0,0 23,16V4A2,2 0 0,0 21,2M3,4H21V16H3M15,5L11.5,8.5L15,12L16.4,10.6L14.3,8.5L16.4,6.4M9,8L7.6,9.4L9.7,11.5L7.6,13.6L9,15L12.5,11.5"/>
      </SvgIcon>
  );
};

// Reference: https://fonts.gstatic.com/s/i/materialiconsoutlined/folder_open/v12/24px.svg
export const FileManagerIcon = (props) => {
  return (
      <SvgIcon {...props}>
        <path
            d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>
      </SvgIcon>
  );
};