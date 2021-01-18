import React from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';


function NavigationBar(props) {

    return (
    <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
        <Navbar.Brand href="#home">Osler Home</Navbar.Brand>
        <Navbar.Collapse>
        <Nav className="mr-auto">
            <Nav.Link href={props.newPatientUrl}>New Patient</Nav.Link>
            <Nav.Link href={props.allPatientsUrl}>All Patients</Nav.Link>
            <Nav.Link href={props.activePatientsUrl}>Active Patients</Nav.Link>
            <Nav.Link href={props.inventoryUrl}>Drug Inventory</Nav.Link>
            {props.displayAppointments && <Nav.Link href={props.appointmentUrl}>Appointments</Nav.Link>}
            {props.displayAttendance && <Nav.Link href={props.attendanceUrl}>Attendance</Nav.Link>}
            <Nav.Link href={props.aboutUrl}>Help</Nav.Link>
        </Nav>
        <Nav>
            {props.displayAdmin && <Nav.Link href={props.adminUrl}>Admin</Nav.Link>}
            <Nav.Link href={props.logoutUrl}>Logout {props.userString}</Nav.Link>
        </Nav>
        </Navbar.Collapse>
    </Navbar>
  );
}

export default NavigationBar;

