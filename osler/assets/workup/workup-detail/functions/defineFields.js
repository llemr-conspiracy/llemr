import dateString from './dateString';

function defineFields(data) {

    const fields =  {
        dob: {
            name: 'Date of Birth',
            value: dateString(data.patient.date_of_birth),                            
        },
        encounter_date: {
            name: 'Encounter Date',
            value: dateString(data.encounter.clinic_day),
        },
        attestation: {
            name: 'Attestation',
            value: data.signer ? `${data.signer}` : 'Not attested',
        },
        age: {
            name: 'Age',
            value: data.patient.age,
        },
        gender: {
            name: 'Gender',
            value: data.patient.gender,
        },
        ethnicity: {
            name: 'Ethnicity',
            value: data.patient.ethnicities.join(', '),
        },
        cc: {
            name: 'Chief Complaint',
            value: data.chief_complaint,
        },
        author: {
            name: 'Author',
            value: `${data.author} (${data.author_type})`,
        },
        other_vol: {
            name: 'Other Volunteer',
            value: data.other_volunteer.join('; '),
        },
        dx: {
            name: 'Diagnosis',
            value: data.diagnosis,
        },
        dx_cat: {
            name: 'Diagnosis Categories',
            value: data.diagnosis_categories.join(', '),
        },
        will_return: {
            name: 'Patient will Return',
            value: data.will_return ? 'yes' : 'no',
        },
        hpi: {
            name: 'HPI',
            value: data.hpi,
        },
        pmh: {
            name: 'PMH',
            value: data.pmh,
        },
        psh: {
            name: 'PSH',
            value: data.psh,
        },
        meds: {
            name: 'Medications',
            value: data.meds,
        },
        allergies: {
            name: 'Allergies',
            value: data.allergies,
        },
        fam_hx: {
            name: 'Family History',
            value: data.fam_hx,
        },
        soc_hx: {
            name: 'Social History',
            value: data.soc_hx,
        },
        ros: {
            name: 'ROS',
            value: data.ros,
        },
        hr: {
            name: 'Heart Rate',
            value: data.rr ? `${data.rr} per min` : '',
        },
        bp: {
            name: 'Blood Pressure',
            value: (data.bp_sys && data.bp_dia) ? `${data.bp_sys}/${data.bp_dia} mmHg` : '',
        },
        rr: {
            name: 'Respiratory Rate',
            value: data.rr ? `${data.rr} per min` : '',
        },
        temp: {
            name: 'Temperature',
            value: data.t ? `${data.t} °C` : '',
        },
        height: {
            name: 'Height',
            value: data.height ? `${data.height} cm` : '',
        },
        weight: {
            name: 'Weight',
            value: data.weight ? `${data.weight} kg` : '',
        },
        pe: {
            name: 'Physical Exam',
            value: data.pe,
        },
        labs_internal: {
            name: 'Labs (Internal)',
            value: data.labs_ordered_internal,
        },
        labs_external: {
            name: 'Labs (External)',
            value: data.labs_ordered_external,
        },
        a_and_p: {
            name: 'A and P',
            value: data.a_and_p,
        },
        rx: {
            name: 'Rx',
            value: data.rx,
        }
    };

    return fields;
}

export default defineFields;