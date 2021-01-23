import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Accordion from 'react-bootstrap/Accordion';
import Row from 'react-bootstrap/Row';
import Container from 'react-bootstrap/Container';
import WorkupSection from './WorkupSection';


function WorkupDetail(props) {

    const [loading, setLoading] = useState(true);
    const [items, setItems] = useState([]);

    useEffect(() => {
        const apiUrl = "/api/workups/" + props.pk;
        axios
            .get(apiUrl)
            .then((response) => {
                const data = response.data;
                console.log(data);

                setItems({
                    at_a_glance: [
                        {
                            name: 'Chief Complaint',
                            value: data.cc,
                        },
                        {
                            name: 'Author',
                            value: `${data.author} ${data.author_type}`,
                        },
                        {
                            name: 'Other Volunteer(s)',
                            value: data.other_volunteer.join('; '),
                        },
                        {
                            name: 'Diagnosis',
                            value: data.diagnosis,
                        },
                        {
                            name: 'Diagnosis Categories',
                            value: data.diagnosis_categories.join('; '),
                        },
                        {
                            name: 'Patient will Return',
                            value: (data.will_return ? 'yes' : 'no'),
                        }
                    ],
                    hp: [
                        {
                            name: 'HPI',
                            value: data.hpi,
                        },
                        {
                            name: 'PMH',
                            value: data.pmh,
                        },
                        {
                            name: 'PSH',
                            value: data.psh,
                        },
                        {
                            name: 'Medications',
                            value: data.meds,
                        },
                        {
                            name: 'Allergies',
                            value: data.allergies,
                        },
                        {
                            name: 'Family History',
                            value: data.fam_hx,
                        },
                        {
                            name: 'Social History',
                            value: data.soc_hx,
                        },
                        {
                            name: 'ROS',
                            value: data.ros,
                        },
                    ],
                });

                setLoading(false);
            });
      }, []);

    return (

        <Container>
            {loading ? (
            <span>Loading...</span>
            ) : (
            <>
            <Row>
                <h4>{'At a Glance'}</h4>
            </Row>
            <Row>
                <WorkupSection items={items.at_a_glance}/>
            </Row>
            <Row>
                <h4>{'H and P'}</h4>
            </Row>
            <Row>
                <WorkupSection items={items.hp}/>
            </Row>
            </>
            )}
        </Container>
    )
}

export default WorkupDetail;