import "regenerator-runtime/runtime";

import React from 'react';
import ReactDOM from 'react-dom';
import NavigationBar from './NavigationBar';


export function render(props) {
    ReactDOM.render(
        <NavigationBar {...props}/>,
        document.getElementById('top-nav-bar')
    );
}
