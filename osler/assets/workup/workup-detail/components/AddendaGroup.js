import React from 'react';
import dateTimeString from '../functions/dateTimeString';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';


function AddendaGroup({addenda}) {

    // show oldest addendum first
    addenda.reverse()

    return (
        <>
        {addenda.map((addendum) => (
        <Row className='mb-3' key={addendum.id}>
            <Col>
                <Card>
                    <Card.Header>
                        {`${addendum.author} (${addendum.author_type}) on ${dateTimeString(addendum.written_datetime)}`}
                    </Card.Header>
                    <Card.Body>{addendum.text ? addendum.text : '(empty)'}</Card.Body>
                </Card>
            </Col>
        </Row>
        ))}
        </>
    );
}

export default AddendaGroup;