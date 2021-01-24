import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Accordion from 'react-bootstrap/Accordion';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Card from 'react-bootstrap/Card';
import CardGroup from 'react-bootstrap/CardGroup';
import CardDeck from 'react-bootstrap/CardDeck';


import WorkupSection from './WorkupSection';



function WorkupDetail(props) {

    const [loading, setLoading] = useState(true);
    const [items, setItems] = useState({
        at_a_glance: [],
        h_and_p: []
    });

    useEffect(() => {
        const apiUrl = "/api/workups/" + props.pk;
        axios
            .get(apiUrl)
            .then((response) => {
                const data = response.data;
                console.log(data);

                const sections = {
                    at_a_glance: [
                        {
                            name: 'Chief Complaint',
                            value: data.chief_complaint,
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
                };


                for (let i = 0; i < sections.at_a_glance.length; i++) {
                    if (i % 3 == 0) {
                        items.at_a_glance.push([]);
                    }
                    let j = Math.floor(i / 3);
                    items.at_a_glance[j].push(sections.at_a_glance[i]);
                }


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
            {items.at_a_glance.map((row) => (
            <Row className='mb-3'>
                {row.map((field) => (
                    <Col md={4} key={field.name}>
                        <Card key={field.name} className='h-100'>
                            <Card.Header>{field.name}</Card.Header>
                            <Card.Body>{field.value}</Card.Body>
                        </Card>
                    </Col>
                ))}
            </Row>
            ))}

            {/* <Row>
                <h4>{'H and P'}</h4>
            </Row>
            <Row>
                <Col md={12} key='h_and_p'>
                    <Accordion>
                    {items.hp.map((item) => (
                        <Card key={item.name}>
                            <Card.Header>{item.name}</Card.Header>
                            <Card.Body>{item.value}</Card.Body>
                        </Card>
                    ))}
                    </Accordion>
                </Col>
            </Row> */}
            </>
            )}
        </Container>
    )
}

export default WorkupDetail;