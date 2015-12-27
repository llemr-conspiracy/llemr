from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from pttrack.test_views import build_provider_and_log_in
from pttrack.models import Patient, ProviderType, Provider

from . import validators
from . import models

BASIC_FIXTURE = 'basic_fixture'

class TestModelFieldValidators(TestCase):
    '''
    TestCase to verify that validators are functioning.
    '''

    def test_validate_bp(self):
        '''
        Test our validator for blood pressures. There should be a '/' between
        systolic and diastolic, it should be able to handle 2 and 3 digit
        pressures, and systolic should always be higher than diastolic.
        '''
        self.assertEqual(validators.validate_bp("110/90"), None)
        self.assertEqual(validators.validate_bp("90/50"), None)
        self.assertEqual(validators.validate_bp("170/100"), None)

        with self.assertRaises(ValidationError):
            validators.validate_bp("90")
        with self.assertRaises(ValidationError):
            validators.validate_bp("/90")
        with self.assertRaises(ValidationError):
            validators.validate_bp("100/")
        with self.assertRaises(ValidationError):
            validators.validate_bp("90/200")
        with self.assertRaises(ValidationError):
            validators.validate_bp("-120/80")

class ViewsExistTest(TestCase):
    '''
    Verify that views involving the wokrup are functioning.
    '''
    fixtures = [BASIC_FIXTURE]

    def setUp(self):

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=now().date(),
            gcal_id="tmp")

        build_provider_and_log_in(self.client)

    def test_clindate_create_redirect(self):
        '''Verify that if no clindate exists, we're properly redirected to a
        clindate create page.'''

        # First delete clindate that's created in setUp.
        models.ClinicDate.objects.all().delete()

        pt = Patient.objects.all()[0]

        pt_url = 'new-workup'
        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('new-clindate', args=(pt.id,)), response.url)

    def test_new_workup_view(self):

        pt = Patient.objects.all()[0]
        response = self.client.get(reverse('new-workup', args=(pt.id,)))
        self.assertEqual(response.status_code, 200)

    def test_workup_urls(self):
        wu_urls = ['workup',
                   'workup-update']

        # test the creation of many workups, just in case.
        for i in range(101):
            wu = models.Workup.objects.create(
                clinic_day=models.ClinicDate.objects.all()[0],
                chief_complaint="SOB",
                diagnosis="MI",
                HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
                ros="", pe="", A_and_P="",
                author=models.Provider.objects.all()[0],
                author_type=ProviderType.objects.all()[0],
                patient=Patient.objects.all()[0])

            wu.diagnosis_categories.add(models.DiagnosisType.objects.all()[0])

            for wu_url in wu_urls:
                # Only actually run the test for every tenth wu for performance
                if i % 10 == 1:
                    response = self.client.get(reverse(wu_url, args=(wu.id,)))
                    self.assertEqual(response.status_code, 200)

    def test_workup_update(self):
        '''
        Updating should be possible always for attendings, only without
        attestation for non-attendings.
        '''
        
        #TODO: pull all these Workup creations into the setup function.
        wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=Provider.objects.all()[0],
            author_type=ProviderType.objects.all()[0],
            patient=Patient.objects.all()[0])

        # if the wu is unsigned, all can access update.
        for role in ["Preclinical", "Clinical", "Coordinator", "Attending"]:
            build_provider_and_log_in(self.client, [role])
            response = self.client.get(reverse('workup-update', args=(wu.id,)))
            self.assertEqual(response.status_code, 200)

        provider = build_provider_and_log_in(self.client, ["Attending"])
        wu.sign(provider.associated_user)
        wu.save()

        #nonattesting cannot access
        for role in ["Preclinical", "Clinical", "Coordinator"]:
            build_provider_and_log_in(self.client, [role])
            response = self.client.get(reverse('workup-update', args=(wu.id,)))
            self.assertRedirects(response, reverse('workup', args=(wu.id,)))

        #attesting can
        build_provider_and_log_in(self.client, ["Attending"])
        response = self.client.get(reverse('workup-update', args=(wu.id,)))
        self.assertEqual(response.status_code, 200)

    def test_workup_signing(self):
        '''
        Verify that singing is possible for attendings, and not for others.
        '''

        wu_url = "workup-sign"

        wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=Provider.objects.all()[0],
            author_type=ProviderType.objects.all()[0],
            patient=Patient.objects.all()[0])

        wu.diagnosis_categories.add(models.DiagnosisType.objects.all()[0])
        wu.save()

        # Fresh workups should be unsigned
        self.assertFalse(wu.signed())

        # Providers with can_attend == False should not be able to sign
        for nonattesting_role in ["Preclinical", "Clinical", "Coordinator"]:
            build_provider_and_log_in(self.client, [nonattesting_role])

            response = self.client.get(reverse(wu_url, args=(wu.id,)))
            self.assertRedirects(response, reverse('workup', args=(wu.id,)))
            self.assertFalse(models.Workup.objects.get(pk=wu.id).signed())

        # Providers able to attend should be able to sign.
        build_provider_and_log_in(self.client, ["Attending"])

        response = self.client.get(reverse(wu_url, args=(wu.id,)))
        self.assertRedirects(response, reverse('workup', args=(wu.id,)),)
        # the wu has been updated, so we have to hit the db again.
        self.assertTrue(models.Workup.objects.get(pk=wu.id).signed())

