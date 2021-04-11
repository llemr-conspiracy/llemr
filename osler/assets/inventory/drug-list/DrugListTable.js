import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TableManager from '../../core/all-patients/TableManager';
import Container from 'react-bootstrap/Container';
import globalFilter from './globalFilter';
import { DateTime } from 'luxon';


function DrugListTable(props) {

  const columns = React.useMemo(
    () => {
      let cols = [
        {
          Header: 'Name',
          accessor: 'name',
        },
        {
          Header: 'Dose',
          accessor: (row) => `${row.dose} ${row.unit}`,
        },
        {
          Header: 'Category',
          accessor: (row) => <strong>{row.category}</strong>
        },
        {
          Header: 'Stock',
          accessor: (row) => <strong>{row.stock}</strong>,
        },
        {
          Header: 'Lot Number',
          accessor: 'lot_number',
        },
        {
          Header: 'Expiration Date',
          accessor: (row) => {
            const dt = DateTime.fromISO(row.expiration_date);
            const options = {
              year: 'numeric', month: 'short', day: 'numeric'
            }
            return dt.toLocaleString(options);
          },
        },
        {
          Header: 'Manufacturer',
          accessor: 'manufacturer',
        },
      ]
      return cols;
    }
    ,
    []
  );

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

  useEffect(() => {
    let apiUrl = "/api/drugs";
    axios
      .get(apiUrl)
      .then((response) => {
        setData(response.data);
        setLoading(false);
      });
  }, []);

  return (
    <Container>
      {loading ? (
        <span>Loading...</span>
      ) : (
        <TableManager
          columns={columns}
          data={data}
          globalFilter={globalFilter}
          id='drug-list-table'
        />
      )}
    </Container>
  );
}

export default DrugListTable
