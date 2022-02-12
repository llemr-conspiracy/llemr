import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TableManager from '../../core/all-patients/TableManager';
import CSRFToken from '../../util/CSRFToken';
import compare from '../../util/compare';
import simpleComparator from '../../util/simpleComparator';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
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
            const now = DateTime.now();
            const options = {
              year: 'numeric', month: 'short', day: 'numeric'
            }
            
            if (dt <= now) {
              return <strong style={{color: "red"}}>{dt.toLocaleString(options)}</strong>
            }
            if (dt <= now.plus({ days: 30})) {
              return <strong style={{color: "gold"}}>{dt.toLocaleString(options)}</strong>
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
                <strong>Dispense</strong>
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
  const [drugs, setDrugs] = useState([]);
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    const drugUrl = "/api/drugs";
    const ptUrl = "/api/patients/?fields=name,age,gender,id&filter=active";
    Promise.all([
      axios.get(drugUrl), 
      axios.get(ptUrl),
    ]).then(function(res) {
      setDrugs(res[0].data);
      setPatients(res[1].data);
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
            data={drugs}
            globalFilter={globalFilter}
            id='drug-list-table'
          />
          <Modal show={state.show} onHide={handleClose}>
            {state.drug &&
              <Form action="/inventory/drug-dispense/" method="post">
                <CSRFToken />
                <Modal.Header closeButton>
                  <Modal.Title>Dispense Drug</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form.Group>
                      <Form.Label>
                        How much <strong>{state.drug.name} {state.drug.dose} {state.drug.unit}</strong> would you like to dispense?
                      </Form.Label>
                      <Form.Control type="number" min={1} max={state.drug.stock} placeholder={1} name="num" id="num"/>
                    </Form.Group>
                    <Form.Group>
                      <Form.Control type="hidden" name="pk" id="pk" value={state.drug.id} />
                    </Form.Group>
                    <Form.Group>
                      <Form.Label>
                        For which patient would you like to dispense <strong>{state.drug.name}</strong>?
                      </Form.Label>
                      <Form.Control as="select" name="patient_pk" id="patient_pk">
                        <option disabled value> -- select patient -- </option>
                        {patients.map(pt => 
                          <option value={pt.id} key={pt.id}>
                            {pt.name} {pt.age}/{pt.gender}
                          </option>
                        )}
                      </Form.Control>
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    Cancel
                </Button>
                <Button variant="primary" type="submit">
                    Dispense Drug
                </Button>
                </Modal.Footer>
              </Form>
            }
          </Modal>
        </>
      )}
    </Container>
  );
}

export default DrugListTable