import React, { useEffect, useState } from 'react';
import axios from 'axios';
import defineFields from '../functions/defineFields';
import Container from 'react-bootstrap/Container';
import SmallFieldGroup from './SmallFieldGroup';
import LargeFieldGroup from './LargeFieldGroup';
import SectionTitle from './SectionTitle';
import AddendaGroup from './AddendaGroup';


/*  TODO account for settings. Current idea is to
 *  have a layout setting returned by API call
 */
function WorkupDetail(props) {

    const [loading, setLoading] = useState(true);
    const [fields, setFields] = useState({});
    const [addenda, setAddenda] = useState({});

    useEffect(() => {

        const apiUrl = `/api/workups/${props.pk}`;
        axios
            .get(apiUrl)
            .then((response) => {
                const data = response.data;
                setFields(defineFields(data));
                setAddenda(data.addendum_set);
                setLoading(false);
            });
      }, []);

    return (
        <Container style={{whiteSpace: 'pre-line'}}>
            {loading ? (
            <span>Loading...</span>
            ) : (
            <>
            <SectionTitle title={'Overview'} />
            <SmallFieldGroup
                fieldSet={[
                    'dob','encounter_date','attestation',
                    'age','gender','ethnicity'
                ]}
                fields={fields}
            />
            <SectionTitle title={'At a Glance'} />
            <SmallFieldGroup 
                fieldSet={[
                    'cc','author','other_vol',
                ]}
                fields={fields}
            />
            <SectionTitle title={'H and P'} />
            <LargeFieldGroup 
                fieldSet={[
                    'hpi','pmh','psh','meds','allergies',
                    'fam_hx','soc_hx','ros'
                ]}
                fields={fields}
            />
            <SectionTitle title={'Vital Signs'} />
            <SmallFieldGroup
                fieldSet={[
                    'hr','bp','rr','temp','height','weight'
                ]}
                fields={fields}
            />
            <LargeFieldGroup 
                fieldSet={['pe']}
                fields={fields}
            />
            <SmallFieldGroup 
                fieldSet={['labs_internal','labs_external']}
                fields={fields}
            />
            <SectionTitle title={'Discharge'} />
            <LargeFieldGroup 
                fieldSet={['a_and_p','rx']}
                fields={fields}
            />
            <SectionTitle title={'Addenda'} />
            <AddendaGroup addenda={addenda} />
            </>
            )}
        </Container>
    )
}

export default WorkupDetail;