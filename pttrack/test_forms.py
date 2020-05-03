from __future__ import unicode_literals
from builtins import str
from builtins import range
import datetime

from django.test import TestCase

from .models import Language, Gender, Ethnicity, ContactMethod, ProviderType, \
    Provider, ActionInstruction, Patient
from . import forms


class TestActionItemCreateForms(TestCase):
    '''Tests for form used to create new Action Items'''

    def setUp(self):
        ai_data = {
            'author': Provider.objects.first(),
            'author_type': ProviderType.objects.first(),
            'patient': Patient.objects.first()
        }
        self.ai_data = ai_data

    def test_instruction_inactive(self):
        '''
        Action Item Form only shows active instructions as options.
        '''
        ai_data = self.ai_data

        PCP_followup = ActionInstruction.objects.create(
            instruction='PCP Followup', active=False)
        Lab_Followup = ActionInstruction.objects.create(
            instruction='Lab Followup', active=True)
        Vaccine_Followup = ActionInstruction.objects.create(
            instruction='Vaccine Followup', active=True)

        ai_qs = ActionInstruction.objects.filter(
            active=True).values_list('instruction', flat=True)

        form = forms.ActionItemForm(data=ai_data)

        form_list = [c[0] for c in form['instruction'].field.choices][1:]

        self.assertEqual(set(ai_qs), set(form_list))

        # Accept active Action Instructions
        ai_data['instruction'] = Lab_Followup.pk
        form = forms.ActionItemForm(data=ai_data)
        self.assertEqual(len(form['instruction'].errors), 0)

        # Reject inactive Action Instructions
        ai_data['instruction'] = PCP_followup.pk
        form = forms.ActionItemForm(data=ai_data)
        self.assertNotEqual(len(form['instruction'].errors), 0)


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
            'date_of_birth': datetime.date(1990, 1, 1),
            'patient_comfortable_with_english': False,
            'ethnicities': [Ethnicity.objects.create(name="Klingon")],
            'preferred_contact_method':
                ContactMethod.objects.create(
                    name="Tin Cans + String").pk,
        }

    def test_form_casemanager_options(self):
        '''
        PatientForm only offers valid case managers as options.
        '''

        casemanager = ProviderType.objects.create(
            long_name='Case Manager', short_name='CM',
            signs_charts=False, staff_view=True)

        not_casemanager = ProviderType.objects.create(
            long_name='Not Case Manager', short_name='NCM',
            signs_charts=False, staff_view=False)

        provider_skeleton = {
            'first_name': "Firstname",
            'last_name': "Lastname",
            'gender': Gender.objects.first(),
        }

        pvds = [Provider.objects.create(
            middle_name=str(i), **provider_skeleton) for i in range(4)]
        pvds[1].clinical_roles.add(not_casemanager)
        pvds[2].clinical_roles.add(casemanager)
        pvds[3].clinical_roles.add(not_casemanager, casemanager)
        [p.save() for p in pvds]

        cm_qs = Provider.objects.filter(
            clinical_roles__in=[casemanager]).values_list('id', flat=True)

        form = forms.PatientForm()

        # c[0] is the pk of each, [1:] indexing required because element 0
        # is the "blank" option.
        form_list = [c[0] for c in form['case_managers'].field.choices]

        # cast to set for 1) order-insensitivity and 2) b/c cm_qs is
        # a queryset and form_list is a list
        self.assertEqual(set(cm_qs), set(form_list))

        # Make sure we reject non-case manager providers

        form_data = self.valid_pt_dict.copy()
        form_data['case_managers'] = [pvds[0]]
        form = forms.PatientForm(data=form_data)
        self.assertNotEqual(len(form['case_managers'].errors), 0)

        form_data = self.valid_pt_dict.copy()
        form_data['case_managers'] = [pvds[1].pk]
        form = forms.PatientForm(data=form_data)
        self.assertNotEqual(len(form['case_managers'].errors), 0)

        # Make sure we accept case manager providers

        form_data = self.valid_pt_dict.copy()
        form_data['case_managers'] = [pvds[2].pk]
        form = forms.PatientForm(data=form_data)
        self.assertEqual(len(form['case_managers'].errors), 0)

        form_data = self.valid_pt_dict.copy()
        form_data['case_managers'] = [pvds[3].pk]
        form = forms.PatientForm(data=form_data)
        self.assertEqual(len(form['case_managers'].errors), 0)

    def test_missing_alt_phone(self):
        '''Missing the alternative phone w/o alt phone owner should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1_owner'] = "Jamal"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)

        # and expect an error to be on the empty altphone field
        self.assertNotEqual(len(form['alternate_phone_1'].errors), 0)

    def test_missing_alt_phone_owner(self):
        '''Missing the alt phone owner w/o alt phone should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1'] = "4258612322"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)
        # we expect errors on the empty alternate_phone_1_owner field
        self.assertNotEqual(len(form['alternate_phone_1_owner'].errors), 0)
