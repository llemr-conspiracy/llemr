import React from 'react';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';


function SmallFieldGroup({fields,fieldSet}) {

    const section = []
    fieldSet.forEach((fieldName) => {
        section.push(fields[fieldName])
    });

    console.log(section);

    const formattedSection = [[]];
    let j = 0;
    let colCount = 0;
    for (let i = 0; i < section.length; i++) {
        // up to three per row, and avoid having a single column on the last row
        if (colCount == 3 || (colCount == 2 && i + 2 == section.length)) {
            formattedSection.push([]);
            colCount = 0;
            j++;
        }
        formattedSection[j].push(section[i]);
        colCount++;
    }

    return (
        <>
        {formattedSection.map((row) => (
            <Row key={row[0].name} className='mb-3'>
                {row.map((field) => (
                    <Col key={field.name}>
                        <Card key={field.name} className='h-100'>
                            <Card.Header>{field.name}</Card.Header>
                            <Card.Body>{field.value ? field.value : '(empty)'}</Card.Body>
                        </Card>
                    </Col>
                ))}
            </Row>
        ))}
        </>
    );
}

export default SmallFieldGroup;