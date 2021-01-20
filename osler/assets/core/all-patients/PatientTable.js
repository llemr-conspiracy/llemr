import axios from 'axios';
import React, { useState, useEffect } from 'react';
import TableManager from './TableManager';


function PatientTable(props) {

  const columns = React.useMemo(
    () => {
      let cols = [
        {
          Header: 'Patient Name',
          accessor: (row) => <a href={row.detail_url}>{row.name}</a>,
        },
        {
          Header: 'Age/Gender',
          accessor: (row) => `${row.age}/${row.gender}`,
        },
        {
          Header: 'Case Managers',
          accessor: (row) => row.case_managers.join('; '),
        },
        {
          Header: 'Latest Activity',
          accessor: (row) => {
            const wu = row.latest_workup;
            if (wu == null) {
              return 'Intake';
            }
            const date = new Date(wu.written_datetime);
            const options = {
              year: 'numeric', month: 'short', day: 'numeric'
            }
            // should default to current locale
            const dateString = date.toLocaleDateString(undefined, options);
            const infoString = wu.is_pending ? "Pending from" : "Seen";
            return (
              <div>
                <a href={wu.detail_url}>{infoString} {dateString}:</a> {wu.chief_complaint}
              </div>
            );
          }
        },
        {
          Header: 'Next AI Due',
          accessor: 'actionitem_status',
        },
        {
          Header: 'Attestation',
          accessor: (row) => {
            const wu = row.latest_workup;
            if (wu == null) {
              return 'No Note';
            }
            if (wu.signer == null) {
              return 'Unattested';
            }
            return wu.signer;
          },
        },
      ]
      if (!props.displayCaseManagers) {
        cols = cols.filter((col) => (col.Header != 'Case Managers'));
      }
      return cols;
    }
    ,
    []
  );

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

  useEffect(() => {
    async function getData() {
      let apiUrl = "/api/patients/?fields=name,age,gender,detail_url,latest_workup,actionitem_status";
      if (props.displayCaseManagers) {
        apiUrl += ",case_managers";
      }
      if (props.activePatients) {
        apiUrl += "&filter=active&sort=encounter__order";
      }
      await axios
        .get(apiUrl)
        .then((response) => {
          setData(response.data);
          setLoading(false);
        });
    }
    if (loading) {
      getData();
    }
  }, []);

  return (
    <div className='container'>
      {loading ? (
        <span>Loading...</span>
      ) : (
          <TableManager columns={columns} data={data} id='all-patients-table' />
        )}
    </div>
  );
}

export default PatientTable;
