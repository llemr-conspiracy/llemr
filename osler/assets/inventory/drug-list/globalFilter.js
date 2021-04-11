function globalFilter(rows, columnIds, globalFilterValue) {
    const filterValue = globalFilterValue.toLowerCase();
    return rows.filter((row) => {
      const name = row.original.name.toLowerCase();
      const lot_number = row.original.lot_number.toLowerCase();
      return (name.includes(filterValue) || lot_number.includes(filterValue));
    });
}

export default globalFilter;