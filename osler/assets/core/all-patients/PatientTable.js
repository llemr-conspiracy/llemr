import axios from 'axios';
import React, { useState, useEffect } from 'react';
import Table from './Table';


function PatientTable(props) {

  const columns = React.useMemo(
    () => [
      {
        Header: 'Patient Name',
        accessor: (row) => <a href={row.detail_url}>{row.name}</a>,
      },
      {
        Header: 'Age/Gender',
        accessor: (row) => `${row.age}/${row.gender}`
      },
      {
        Header: 'Latest Activity',
        accessor: (row) => {
          const wu = row.latest_workup;
          if (wu == null) {
            return 'Intake';
          }
          else {
            const date = new Date(wu.written_datetime);
            const options = {
              year: 'numeric', month: 'short', day: 'numeric'
            }
            // should default to current locale
            const dateString = date.toLocaleDateString(undefined,options);
            return (
              // wrap in div to combine string and href
              <div>
                <a href={wu.detail_url}>Seen {dateString}:</a> {wu.chief_complaint}
              </div>
            );
          }
        }
      },
    ],
    []
  )
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

  useEffect(() => {
    let apiUrl = "/api/patient/?fields=name,age,gender,detail_url,latest_workup";
    if (props.activePatients) {
      apiUrl += "&filter=active";
    }
    async function getData() {
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
        <p>Loading, please wait...</p>
      ) : (
        <Table columns={columns} data={data} />
      )}
    </div>
  );

}

export default PatientTable;
