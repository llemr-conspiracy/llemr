import datetime

from django.test import TestCase

from .models import Language, Gender, Ethnicity, ContactMethod, Patient
from . import forms


class TestPatientCreateForms(TestCase):
    '''Tests for the form used to create new Patients.'''

    def setUp(self):

        self.valid_pt_dict = {
            'first_name': "Juggie",
            'last_name': "Brodeltein",
            'middle_name': "Bayer",
            'phone': '+49 178 236 5288',
            'languages': [Language.objects.create(name="Klingon")],
            'gender': Gender.objects.create(
                long_name="Male", short_name="M").pk,
            'address': 'Schulstrasse 9',
            'city': 'Munich',
            'state': 'BA',
            'country': 'Germany',
            'zip_code': '63108',
            'pcp_preferred_zip': '63018',
            'date_of_birth': datetime.date(1990, 01, 01),
            'patient_comfortable_with_english': False,
            'ethnicities': [Ethnicity.objects.create(name="Klingon")],
            'preferred_contact_method':
                ContactMethod.objects.create(
                    name="Tin Cans + String").pk,
        }

    def test_create_ssn(self):
        '''Verify that SSNs are cleaned in the form properly.'''

        form_data = self.valid_pt_dict
        form_data['ssn'] = '001121234'

        form = forms.PatientForm(data=form_data)
        self.assertNotEqual(form['ssn'].errors, [])

        form_data = self.valid_pt_dict
        form_data['ssn'] = '001-12-1234'

        form = forms.PatientForm(data=form_data)
        self.assertEqual(form['ssn'].errors, [])
        self.assertEqual(form['ssn'].data, '001-12-1234')

        form.save()

        self.assertEqual(Patient.objects.last().ssn, form['ssn'].data)

    def test_missing_alt_phone(self):
        '''Missing the alternative phone w/o alt phone owner should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1_owner'] = "Jamal"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)

        # and expect an error to be on the empty altphone field
        self.assertNotEqual(form['alternate_phone_1'].errors, [])

    def test_missing_alt_phone_owner(self):
        '''Missing the alt phone owner w/o alt phone should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1'] = "4258612322"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)
        # we expect errors on the empty alternate_phone_1_owner field
        self.assertNotEqual(form['alternate_phone_1_owner'].errors, [])

    def test_stray_name_space(self):
        '''Name ending with a space should fail.'''
        form_data = self.valid_pt_dict

        form_data['last_name'] = "Brodeltein "
        # name ends with a space, should get an error

        form = forms.PatientForm(data=form_data)
        # we expect errors on the last_name field
        self.assertNotEqual(form['last_name'].errors, [])
