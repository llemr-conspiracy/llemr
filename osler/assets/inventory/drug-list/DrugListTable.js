import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TableManager from '../../core/all-patients/TableManager';
import compare from '../../core/all-patients/compare';
import simpleComparator from '../../core/all-patients/simpleComparator';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import globalFilter from './globalFilter';
import { DateTime } from 'luxon';


function DrugListTable(props) {

  const [state, setState] = useState({ 'show': false, 'drug': {} });

  const handleClose = () => {
    setState({ 'show': false, 'drug': {} });
  }
  const handleShow = (e, row) => {
    setState({ 'show': true, 'drug': row });
  }

  const nameComparator = simpleComparator('name');
  const categoryComparator = simpleComparator('category');
  const expirationDateComparator = simpleComparator('expiration_date');
  const stockComparator = simpleComparator('stock');
  const doseComparator = React.useMemo(() => (rowA,rowB,columnId,desc) => {
    let cmp = compare(rowA.original.unit,rowB.original.unit);
    if (cmp == 0) {
      cmp = compare(rowA.original.dose, rowB.original.dose);
    }
    return cmp;
  });

  const columns = React.useMemo(
    () => {
      let cols = [
        {
          Header: 'Name',
          accessor: 'name',
          sortType: nameComparator,
        },
        {
          Header: 'Dose',
          accessor: (row) => `${row.dose} ${row.unit}`,
          sortType: doseComparator,
        },
        {
          Header: 'Category',
          accessor: (row) => <strong>{row.category}</strong>,
          sortType: categoryComparator,
        },
        {
          Header: 'Stock',
          accessor: (row) => <strong>{row.stock}</strong>,
          sortType: stockComparator,
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
          sortType: expirationDateComparator,
        },
        {
          Header: 'Manufacturer',
          accessor: 'manufacturer',
        },
        {
          Header: 'Dispense',
          accessor: (row) => {
            return (
              <Button variant="success" onClick={e => handleShow(e, row)}>
                Dispense
              </Button>
            );
          },
          disableSortBy: true,
        }
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
        <>
          <TableManager
            columns={columns}
            data={data}
            globalFilter={globalFilter}
            id='drug-list-table'
          />
          <Modal show={state.show} onHide={handleClose}>
            {state.drug &&
              <>
                <Modal.Header closeButton>
                  <Modal.Title>Dispense Drug</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                  How much <strong>{state.drug.name} {state.drug.dose} {state.drug.unit}</strong> would you like to dispense?
                </Modal.Body>
                <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    Cancel
                </Button>
                <Button variant="primary" onClick={handleClose}>
                    Dispense Drug
                </Button>
                </Modal.Footer>
              </>
            }
          </Modal>
        </>
      )}
    </Container>
  );
}

export default DrugListTable
