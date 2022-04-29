import {openInNewWindow} from '../../../actions/utils';

const LinkForNewWindow = (props) => (
    <a href={''} onClick={(ev)=>{openInNewWindow(props.url, ev)}}
       style={{wordWrap: 'break-word'}}>
      {props.children}
    </a>);

export default LinkForNewWindow;