import axios from 'axios';
import React, { useState, useEffect } from 'react';
import Table from './Table';



function PatientTable() {

  const columns = React.useMemo(
    () => [
      {
        Header: 'Name',
        columns: [
          {
            Header: 'First Name',
            accessor: 'firstName',
          },
          {
            Header: 'Last Name',
            accessor: 'lastName',
          },
        ],
      },
      {
        Header: 'Info',
        columns: [
          {
            Header: 'Age',
            accessor: 'age',
          },
          {
            Header: 'Visits',
            accessor: 'visits',
          },
          {
            Header: 'Status',
            accessor: 'status',
          },
          {
            Header: 'Profile Progress',
            accessor: 'progress',
          },
        ],
      },
    ],
    []
  )
  
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState([])

  useEffect(() => {
    async function getData() {
      await axios
        .get("/api/patient/?fields=name,age,gender,latest_workup")
        .then((response) => {
          // check if the data is populated
          console.log(response.data);
          setData(response.data);
          // you tell it that you had the result
          setLoading(false);
        });
    }
    if (loading) {
      // if the result is not ready so you make the axios call
      getData();
    }
  }, []);

  return (
    <div>
      {/* here you check if the state is loading otherwise if you will not call that you will get a blank page because the data is an empty array at the moment of mounting */}
      {loading ? (
        <p>Loading Please wait...</p>
      ) : (
        <Table columns={columns} data={data} />
      )}
    </div>
  );

}

export default PatientTable;
