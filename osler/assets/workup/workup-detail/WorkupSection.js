import React from 'react';
import Accordion from 'react-bootstrap/Accordion';
import Card from 'react-bootstrap/Card';
import Col from 'react-bootstrap/Col';


function WorkupSection(items) {

    return (
        <Col md={12}>
        <Accordion>
        {items.items.map((item) => (
            <Card key={item.name}>
                <Card.Header>{item.name}</Card.Header>
                <Card.Body>{item.value}</Card.Body>
            </Card>
        ))}
        </Accordion>
        </Col>
    );
}

export default WorkupSection;