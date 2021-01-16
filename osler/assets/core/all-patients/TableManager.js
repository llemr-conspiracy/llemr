import React from 'react';
import { useTable, useGlobalFilter, usePagination } from 'react-table';
import SearchBar from './SearchBar';
import NavigationBar from './NavigationBar';
import Table from 'react-bootstrap/Table';


function globalFilter(rows, columnIds, globalFilterValue) { 
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

function TableManager({ columns, data, id }) {

    // mainly follow official example from react-table
    const {
      getTableProps,
      getTableBodyProps,
      headerGroups,
      prepareRow,
      page,
      state,
      setGlobalFilter,
      canPreviousPage,
      canNextPage,
      pageOptions,
      pageCount,
      gotoPage,
      nextPage,
      previousPage,
    } = useTable({
      columns,
      data,
      globalFilter: globalFilter,
      initialState: { pageIndex: 0 },
    },
      useGlobalFilter,
      usePagination,
    );
  
    return (
      <div>
      <SearchBar
        globalFilter={state.globalFilter}
        setGlobalFilter={setGlobalFilter}
      />
      <Table {...getTableProps()} id={id}>
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
          {page.map((row, i) => {
            prepareRow(row)
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => {
                  return <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                })}
              </tr>
            );
          })}
        </tbody>
      </Table>
      <NavigationBar
        gotoPage={gotoPage}
        previousPage={previousPage}
        nextPage={nextPage}
        pageIndex={state.pageIndex}
        canPreviousPage={canPreviousPage}
        canNextPage={canNextPage}
        pageOptions={pageOptions}
        pageCount={pageCount}
      />
      </div>
    )
}

export default TableManager;