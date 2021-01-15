import React from 'react';
import { useTable, useGlobalFilter } from 'react-table'
import SearchBar from './SearchBar'


function globalFilter(rows, columnIds, globalFilterValue) {
  // ignore required columnsIds argument
  return rows.filter((row) => {
    const name = row.original.name;
    if (name.includes(globalFilterValue)) {
      return true;
    }
    else if (row.original.hasOwnProperty('case_managers')) {
      const case_managers = row.original.case_managers;
      for (const case_manager of case_managers) {
        if (case_manager.includes(globalFilterValue)) {
          return true;
        }
      }
    }
    return false;
  });
}

function Table({ columns, data, id }) {

    const {
      getTableProps,
      getTableBodyProps,
      headerGroups,
      rows,
      prepareRow,
      state,
      setGlobalFilter,
    } = useTable({
      columns,
      data,
      'globalFilter': globalFilter,
    },
      useGlobalFilter,
    );
  
    return (
      <>
      <SearchBar
        globalFilter={state.globalFilter}
        setGlobalFilter={setGlobalFilter}
      />
      <table {...getTableProps()} className='table' id={id}>
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map((row, i) => {
            prepareRow(row)
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => {
                  return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
      </>
    )
}

export default Table;