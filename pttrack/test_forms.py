'''Module for testing the various custom forms used in Osler.'''

import datetime

from django.test import TestCase

from . import forms
from . import models
from . import followup_models

# pylint: disable=invalid-name

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
        models.ReferralLocation.objects.create(
            name="Franklin's Back Adjustment",
            address="1435 Sillypants Drive")
        followup_models.NoAptReason.objects.create(
            name="better things to do")


    def build_form(self, contact_successful, has_appointment, apt_location, noapt_reason):
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
            'has_appointment': has_appointment,
            }

        if apt_location:
            form_data['apt_location'] = models.ReferralLocation.objects.all()[0]

        if noapt_reason:
            form_data['noapt_reason'] = followup_models.NoAptReason.objects.all()[0]

        return forms.ReferralFollowup(data=form_data)

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
            noapt_reason=True)

        self.assertEqual(len(form['noapt_reason'].errors), 0)

    def test_incorrect_successful_noapt(self):
        '''
        Test that a successful contact with no appointment that lacks a
        noapt_reason is considered incorrect.
        '''

        form = self.build_form(
            contact_successful=True,
            has_appointment=False,
            noapt_reason=False,
            apt_location=False)

        self.assertGreater(len(form['noapt_reason'].errors), 0)

    def test_correct_unsuccssful_noapt(self):
        '''
        Test that an unsuccessful contact requires only has_appointment and
        referral_type. apt_location and noapt_reason are not required.
        '''

        form = self.build_form(
            contact_successful=False,
            has_appointment=False,
            apt_location=False,
            noapt_reason=False)

        self.assertEqual(len(form['noapt_reason'].errors), 0)
