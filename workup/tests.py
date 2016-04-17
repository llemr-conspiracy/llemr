from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from pttrack.test_views import build_provider, log_in_provider
from pttrack.models import Patient, ProviderType, Provider, ReferralLocation, ReferralType

from . import validators
from . import models
from . import forms

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
    fixtures = ['workup', 'pttrack']

    def setUp(self):

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=now().date(),
            gcal_id="tmp")

        log_in_provider(self.client, build_provider())

    def test_clindate_create_redirect(self):
        '''Verify that if no clindate exists, we're properly redirected to a
        clindate create page.'''

        # First delete clindate that's created in setUp.
        models.ClinicDate.objects.all().delete()

        pt = Patient.objects.all()[0]

        pt_url = 'new-workup'
        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('new-clindate', args=(pt.id,)))

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
            log_in_provider(self.client, build_provider([role]))
            response = self.client.get(reverse('workup-update', args=(wu.id,)))
            self.assertEqual(response.status_code, 200)

        wu.sign(build_provider(["Attending"]).associated_user)
        wu.save()

        #nonattesting cannot access
        for role in ["Preclinical", "Clinical", "Coordinator"]:
            log_in_provider(self.client, build_provider([role]))
            response = self.client.get(reverse('workup-update', args=(wu.id,)))
            self.assertRedirects(response, reverse('workup', args=(wu.id,)))

        #attesting can
        log_in_provider(self.client, build_provider(["Attending"]))
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
            log_in_provider(self.client, build_provider([nonattesting_role]))

            response = self.client.get(reverse(wu_url, args=(wu.id,)))
            self.assertRedirects(response, reverse('workup', args=(wu.id,)))
            self.assertFalse(models.Workup.objects.get(pk=wu.id).signed())

        # Providers able to attend should be able to sign.
        log_in_provider(self.client, build_provider(["Attending"]))

        response = self.client.get(reverse(wu_url, args=(wu.id,)))
        self.assertRedirects(response, reverse('workup', args=(wu.id,)),)
        # the wu has been updated, so we have to hit the db again.
        self.assertTrue(models.Workup.objects.get(pk=wu.id).signed())

    def test_workup_pdf(self):
        '''
        Verify that pdf download with the correct naming protocol is working
        '''

        from pttrack.models import Gender, ContactMethod
        
        wu_url = "workup-pdf"

        pt1 = Patient.objects.create(
            first_name="Juggie ",
            last_name="Brodeltein ",
            middle_name="Bayer ",
            phone='+49 178 236 5288',
            gender=Gender.objects.all()[1],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=date(1990, 01, 01),
            patient_comfortable_with_english=False,
            needs_workup=True,
            preferred_contact_method=ContactMethod.objects.all()[0],
        )

        wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=Provider.objects.all()[0],
            author_type=ProviderType.objects.all()[0],
            patient=pt1,
            )

        wu.diagnosis_categories.add(models.DiagnosisType.objects.all()[0])
        wu.save()

        for nonstaff_role in ["Preclinical", "Clinical", "Attending"]:
            log_in_provider(self.client, build_provider([nonstaff_role]))

            response = self.client.get(reverse(wu_url, args=(wu.id,)))
            self.assertRedirects(response, reverse('workup', args=(wu.id,)))

        log_in_provider(self.client, build_provider(["Coordinator"]))
        response = self.client.get(reverse(wu_url, args=(wu.id,)))
        self.assertEqual(response.status_code, 200)

class TestFormFieldValidators(TestCase):
    
    fixtures = ['workup', 'pttrack']

    def setUp(self):
        log_in_provider(self.client, build_provider())

        models.ClinicType.objects.create(name="Basic Care Clinic")
        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=now().date(),
            gcal_id="tmp")


        self.valid_pt_dict = {
            'clinic_day': models.ClinicDate.objects.all()[0],
            'chief_complaint': "SOB",
            'diagnosis': "MI",
            'HPI': "f", 'PMH_PSH': "f", 'meds': "f", 'allergies': "f", 'fam_hx': "f", 'soc_hx': "f",
            'ros': "f", 'pe': "f", 'A_and_P': "f",
            'hr': '89', 'bp': '120/80', 'rr': '16', 't': '98',
            'labs_ordered_internal': 'f', 'labs_ordered_quest': 'f',
            'got_voucher': True,
            'got_imaging_voucher': True,
            'will_return': True,
            'author': Provider.objects.all()[0],
            'author_type': ProviderType.objects.all()[0],
            'patient': Patient.objects.all()[0]
        }

    def test_missing_voucher_amount(self):

        form_data = self.valid_pt_dict

        form = forms.WorkupForm(data=form_data)

        # and expect an error to be on the empty altphone field
        self.assertNotEqual(form['voucher_amount'].errors, [])
        self.assertNotEqual(form['patient_pays'].errors, [])
        
        form_data['voucher_amount'] = '40'
        form_data['patient_pays'] = '40'

        form = forms.WorkupForm(data=form_data)
        self.assertEqual(form['voucher_amount'].errors, [])
        self.assertEqual(form['patient_pays'].errors, [])

        self.assertNotEqual(form['imaging_voucher_amount'].errors, [])
        self.assertNotEqual(form['patient_pays_imaging'].errors, [])

        form_data['imaging_voucher_amount'] = '40'
        form_data['patient_pays_imaging'] = '40'

        form = forms.WorkupForm(data=form_data)
        self.assertEqual(form['imaging_voucher_amount'].errors, [])
        self.assertEqual(form['patient_pays_imaging'].errors, [])

class AttendingTests(TestCase):
    fixtures = ['pttrack', 'workup']

    def setUp(self):
        log_in_provider(self.client, build_provider(["Attending"]))

    def test_home_has_correct_patients_attending(self):

        # TODO: probably, the solution is a "home" app.
        from pttrack.models import Gender, ContactMethod

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=now(),
            gcal_id="435345")
        # we need > 1 pt, because one will have an active AI and one won't
        pt1 = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.all()[1],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=date(1990, 01, 01),
            patient_comfortable_with_english=False,
            needs_workup=True,
            preferred_contact_method=ContactMethod.objects.all()[0],
        )

        pt2 = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.all()[1],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=date(1990, 01, 01),
            patient_comfortable_with_english=True,
            needs_workup=True,
            preferred_contact_method=ContactMethod.objects.all()[0],
        )

        pt3 = Patient.objects.create(
            first_name="asdf",
            last_name="lkjh",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.all()[0],
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=date(1990, 01, 01),
            patient_comfortable_with_english=False,
            needs_workup=True,
            preferred_contact_method=ContactMethod.objects.all()[0],
        )

        wu1 = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=Provider.objects.all()[0],
            author_type=ProviderType.objects.all()[0],
            patient=pt1)

        wu2 = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=Provider.objects.all()[0],
            author_type=ProviderType.objects.all()[0],
            patient=pt2,
            signer=Provider.objects.all().filter(
                clinical_roles=ProviderType.objects.all().filter(
                    short_name="Attending")[0])[0])

        wu3 = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            author=models.Provider.objects.all()[0],
            author_type=ProviderType.objects.all()[0],
            patient=pt3)

        url = reverse("home")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # pt1, pt3 should be present since they are not signed
        self.assertEqual(len(response.context['zipped_list'][0][1]), 2)
        self.assertIn(pt1, response.context['zipped_list'][0][1])
        self.assertIn(pt3, response.context['zipped_list'][0][1])
