import "regenerator-runtime/runtime";

import React from 'react';
import ReactDOM from 'react-dom';
import PatientTable from './PatientTable';

export function render(props) {
    ReactDOM.render(
        <PatientTable {...props}/>,
        document.getElementById('root')
    );
}
