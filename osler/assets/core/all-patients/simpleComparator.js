import compare from './compare';
import React from 'react';

const simpleComparator = (field) => React.useMemo(
() => (rowA,rowB,columnId,desc) => compare(rowA.original[field],rowB.original[field]));

export default simpleComparator;