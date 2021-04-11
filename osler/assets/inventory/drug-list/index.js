import "regenerator-runtime/runtime";

import React from 'react';
import ReactDOM from 'react-dom';
import DrugListTable from './DrugListTable';


export function render(props) {
    ReactDOM.render(
        <DrugListTable {...props} />,
        document.getElementById('root')
    );
}