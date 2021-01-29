import React from 'react';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';


function LargeFieldGroup({fields,fieldSet}) {

    const section = []
    fieldSet.forEach((fieldName) => {
        section.push(fields[fieldName])
    });

    return (
        <>
        {section.map((field) => (
        <Row className='mb-3' key={field.name}>
            <Col>
                <Card>
                    <Card.Header>{field.name}</Card.Header>
                    <Card.Body>{field.value ? field.value : '(empty)'}</Card.Body>
                </Card>
            </Col>
        </Row>
        ))}
        </>
    );
}

export default LargeFieldGroup;