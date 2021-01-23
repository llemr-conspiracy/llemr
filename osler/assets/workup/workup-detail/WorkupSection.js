import React from 'react';
import Accordion from 'react-bootstrap/Accordion';
import Card from 'react-bootstrap/Card';


function WorkupSection(items) {

    return (
        <Accordion>
        {items.items.map((item) => (
            <Card key={item.name}>
                <Card.Header>{item.name}</Card.Header>
                <Card.Body>{item.value}</Card.Body>
            </Card>
        ))}
        </Accordion>
    );
}

export default WorkupSection;