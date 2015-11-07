'''Module for testing the various custom forms used in Osler.'''

import datetime

from django.test import TestCase

from . import forms
from . import models
from . import followup_models

# pylint: disable=invalid-name

BASIC_FIXTURE = 'basic_fixture'

class TestPatientCreateForms(TestCase):
    '''Tests for the form used to create new Patients.'''

    def setUp(self):

        self.valid_pt_dict = {
            'first_name': "Juggie",
            'last_name': "Brodeltein",
            'middle_name': "Bayer",
            'phone': '+49 178 236 5288',
            'languages': [models.Language.objects.create(name="Klingon")],
            'gender': models.Gender.objects.create(
                long_name="Male", short_name="M").pk,
            'address': 'Schulstrasse 9',
            'city': 'Munich',
            'state': 'BA',
            'country': 'Germany',
            'zip_code': '63108',
            'pcp_preferred_zip': '63018',
            'date_of_birth': datetime.date(1990, 01, 01),
            'patient_comfortable_with_english': False,
            'ethnicities': [models.Ethnicity.objects.create(name="Klingon")],
            'preferred_contact_method':
                models.ContactMethod.objects.create(
                    name="Tin Cans + String").pk,
        }

    def test_missing_alt_phone(self):
        '''Missing the alternative phone w/o alt phone owner should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1_owner'] = "Jamal"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)
        self.assertEqual(form['first_name'].errors, [])
        self.assertNotEqual(form['alternate_phone_1_owner'].errors, [])

    def test_missing_alt_phone_owner(self):
        '''Missing the alt phone owner w/o alt phone should fail.'''
        form_data = self.valid_pt_dict

        form_data['alternate_phone_1'] = "4258612322"
        # omit 'alternate_phone', should get an error

        form = forms.PatientForm(data=form_data)
        self.assertEqual(form['first_name'].errors, [])
        self.assertNotEqual(form['alternate_phone_1'].errors, [])


class TestReferralFollowupForms(TestCase):
    '''
    Test the validation and behavior of the forms used to do followups.
    '''
    
    def setUp(self):
        self.contact_method = models.ContactMethod.objects.create(
            name="Carrier Pidgeon")

        self.pt = models.Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=models.Gender.objects.create(long_name="Male",
                                                short_name="M"),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 01, 01),
            patient_comfortable_with_english=False,
            preferred_contact_method=self.contact_method,
        )

        self.successful_res = followup_models.ContactResult.objects.create(
            name="Got him", patient_reached=True)
        self.unsuccessful_res = followup_models.ContactResult.objects.create(
            name="Disaster", patient_reached=False)
        self.reftype = models.ReferralType.objects.create(name="Chiropracter")
        self.referral_location = models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        self.noapt_reason = followup_models.NoAptReason.objects.create(
            name="better things to do")
        self.noshow_reason = followup_models.NoShowReason.objects.create(
            name="Hella busy.")


    def build_form(self, contact_successful, has_appointment, apt_location, noapt_reason, noshow_reason, pt_showed=None):
        '''
        Construct a ReferralFollowup form to suit the needs of the testing
        subroutines based upon what is provided and not provided.
        '''

        contact_resolution = self.successful_res if contact_successful else self.unsuccessful_res

        form_data = {
            'contact_method': self.contact_method,
            'contact_resolution': contact_resolution,
            'patient': self.pt,
            'referral_type': self.reftype,
            }

        # Has appointment could (at least in principle) be True, False, or
        # unspecified.
        if has_appointment:
            form_data['has_appointment'] = True
        elif has_appointment is None:
            pass
        else:
            form_data['has_appointment'] = False

        if apt_location:
            form_data['apt_location'] = self.referral_location.id

        if noapt_reason:
            form_data['noapt_reason'] = self.noapt_reason

        if pt_showed is None:
            pass
        elif pt_showed:
            form_data['pt_showed'] = 'Yes'
        else:
            form_data['pt_showed'] = 'No'

        if noshow_reason:
            form_data['noshow_reason'] = self.noshow_reason


        return forms.ReferralFollowup(data=form_data)

    def test_hasapt_pt_noshow(self):
        '''
        Test correct submission variations for a ReferralFollowup that has an
        appointment.
        '''

        # correct: pt didn't show, noshow reason is supplied
        form = self.build_form(
            contact_successful=True,
            has_appointment=True,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed=False)

        self.assertEqual(len(form.errors), 0)

        # incorrect: pt didn't show and noshow reason is missing
        form = self.build_form(
            contact_successful=True,
            has_appointment=True,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=False,
            pt_showed=False)

        self.assertGreater(len(form['noshow_reason'].errors), 0)

        # incorrect: pt showed and noshow reason is present
        form = self.build_form(
            contact_successful=True,
            has_appointment=True,
            apt_location=True,
            noapt_reason=False,
            noshow_reason=True,
            pt_showed=True)

        self.assertGreater(len(form['noshow_reason'].errors), 0)


    def test_correct_successful_noapt(self):
        '''
        Test a correct submission of ReferralFollowup when
        ContactResult.patient_reached is True but has_appointment is false.
        That is, apt_location and noapt_reason are provided.
        '''

        form = self.build_form(
            contact_successful=True,
            has_appointment=False,
            apt_location=True,
            noapt_reason=True,
            noshow_reason=False)

        self.assertEqual(len(form.errors), 0)

    def test_incorrect_successful_noapt(self):
        '''
        Test that a successful contact with no appointment that lacks a
        noapt_reason is considered incorrect.
        '''

        form = self.build_form(
            contact_successful=True,
            has_appointment=False,
            noapt_reason=False,
            apt_location=False,
            noshow_reason=False)

        self.assertGreater(len(form['noapt_reason'].errors), 0)

    def test_correct_unsuccssful_noapt(self):
        '''
        Test that an unsuccessful contact requires only has_appointment and
        referral_type. apt_location and noapt_reason are not required.
        '''

        form = self.build_form(
            contact_successful=False,
            has_appointment=None,
            apt_location=False,
            noapt_reason=False,
            noshow_reason=False)

        self.assertEqual(len(form.errors), 0)
