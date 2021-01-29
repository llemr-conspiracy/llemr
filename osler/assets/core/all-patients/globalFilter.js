function globalFilter(rows, columnIds, globalFilterValue) {
    const filterValue = globalFilterValue.toLowerCase();
    return rows.filter((row) => {
      const name = row.original.name.toLowerCase();
      if (name.includes(filterValue)) {
        return true;
      } else if (row.original.hasOwnProperty("case_managers")) {
        const case_managers = row.original.case_managers;
        for (const case_manager of case_managers) {
          if (case_manager.toLowerCase().includes(filterValue)) {
            return true;
          }
        }
      }
      return false;
    });
}

export default globalFilter;