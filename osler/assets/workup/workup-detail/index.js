import "regenerator-runtime/runtime";

import React from 'react';
import ReactDOM from 'react-dom';
import WorkupDetail from './components/WorkupDetail';


export function render(props) {
    ReactDOM.render(
        <WorkupDetail {...props} />,
        document.getElementById('root')
    );
}
