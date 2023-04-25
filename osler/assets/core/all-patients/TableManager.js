import React from "react";
import { useTable, useGlobalFilter, usePagination, useSortBy } from "react-table";
import SearchBar from "./SearchBar";
import PaginationBar from "./PaginationBar";
import Table from "react-bootstrap/Table";
import { BsArrowUp, BsArrowDown } from "react-icons/bs"

function TableManager({ columns, data, globalFilter, id }) {

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
  } = useTable(
    {
      columns,
      data,
      globalFilter: globalFilter,
      initialState: { 
        pageIndex: 0,
      },
    },
    useGlobalFilter,
    useSortBy,
    usePagination,
  );

  return (
    <div>
      {<SearchBar
        globalFilter={state.globalFilter}
        setGlobalFilter={setGlobalFilter}
      />}
      <Table {...getTableProps()} id={id}>
        <thead>
          {headerGroups.map((headerGroup) => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                  {column.render("Header")}
                  {column.isSorted &&
                    <span>
                      {column.isSortedDesc
                        ? <BsArrowDown />
                        : <BsArrowUp />
                      }
                    </span>
                  }
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {page.map((row, i) => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map((cell) => {
                  return (
                    <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </Table>
      <PaginationBar
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
  );
}

export default TableManager;
