from django.test import TestCase
from . import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import Client

import datetime


class CustomFuncTesting(TestCase):
    def test_validate_zip(self):
        self.assertEqual(models.validate_zip(12345), None)
        with self.assertRaises(ValidationError):
            models.validate_zip(123456)
        with self.assertRaises(ValidationError):
            models.validate_zip('ABCDE')

    # def test_forms(self):
    #     response = self.client.post('pttrack/intake.html',
    #                                 {'something': 'something'})
    #     self.assertFormError(response, 'PatientForm', 'something',
    #                          'This field is required.')


class ViewsExistTest(TestCase):
    def setUp(self):

        g = models.Gender.objects.create(long_name="Male", short_name="M")
        l = models.Language.objects.create(name="English")
        e = models.Ethnicity.objects.create(name="White")

        models.Patient.objects.create(
            first_name="Frankie", middle_name="Lane", last_name="McNath",
            address="6310 Scott Ave", city="St. Louis", state="MO",
            date_of_birth=datetime.date(year=1989, month=8, day=9),
            phone="501-233-1234",
            language=l,
            ethnicity=e,
            gender=g)

        models.ClinicType.objects.create(name="Basic Care Clinic")

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=datetime.datetime.today(),
            gcal_id="tmp")

        models.DiagnosisType.objects.create(name="Cardiovascular")

        for lname in ["Attending Physician", "Preclinical Medical Student",
                      "Clinical Medical Student", "Coordinator"]:
            models.ProviderType.objects.create(long_name=lname,
                                               short_name=lname.split()[0])

        models.Provider.objects.create(
            first_name="Tommy", middle_name="Lee", last_name="Jones",
            phone="425-243-9115", gender=g, email="tljones@wustl.edu",
            can_attend=True)

    def test_basic_urls(self):
        basic_urls = ["home",
                      "all-patients",
                      "intake"]

        for basic_url in basic_urls:
            response = self.client.get(reverse(basic_url))
            self.assertEqual(response.status_code, 200)

    def test_pt_urls(self):
        pt_urls = ['patient-detail',
                   "new-clindate",
                   'new-action-item',
                   'followup-choice',
                   'new-workup']
        pt = models.Patient.objects.all()[0]

        for pt_url in pt_urls:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 200)

    def test_clindate_create_redirect(self):
        '''Verify that if no clindate exists, we're properly redirected to a
        clindate create page.'''

        # First delete clindate that's created in setUp.
        models.ClinicDate.objects.all().delete()

        pt = models.Patient.objects.all()[0]

        pt_url = 'new-workup'
        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('new-clindate', args=(pt.id,)), response.url)

    def test_workup_urls(self):
        wu_urls = ['workup',
                   'workup-update']

        wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            diagnosis_category=models.DiagnosisType.objects.all()[0],
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=models.Patient.objects.all()[0])

        for wu_url in wu_urls:
            response = self.client.get(reverse(wu_url, args=(wu.id,)))
            self.assertEqual(response.status_code, 200)

    def test_workup_signing(self):

        wu_url = "workup-sign"

        wu = models.Workup.objects.create(
            clinic_day=models.ClinicDate.objects.all()[0],
            chief_complaint="SOB",
            diagnosis="MI",
            HPI="", PMH_PSH="", meds="", allergies="", fam_hx="", soc_hx="",
            ros="", pe="", A_and_P="",
            diagnosis_category=models.DiagnosisType.objects.all()[0],
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=models.Patient.objects.all()[0])

        # Fresh workups should be unsigned
        self.assertFalse(wu.signed())

        # Providers with can_attend == False should not be able to sign
        models.Provider.objects.all()[0].can_attend = False

        response = self.client.get(reverse(wu_url, args=(wu.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(wu.signed())

        # Providers able to attend should be able to sign.
        models.Provider.objects.all()[0].can_attend = True

        response = self.client.get(reverse(wu_url, args=(wu.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(wu.signed())

    def test_action_item_urls(self):
        ai_urls = ['done-action-item',
                   'reset-action-item']

        pt = models.Patient.objects.all()[0]

        ai_inst = models.ActionInstruction.objects.create(
            instruction="Follow up on labs")
        ai = models.ActionItem.objects.create(
            instruction=ai_inst,
            due_date=datetime.datetime.today(),
            comments="",
            author=models.Provider.objects.all()[0],
            author_type=models.ProviderType.objects.all()[0],
            patient=pt)

        # new action items should not be done
        self.assertFalse(ai.done())

        # submit a request to mark the new ai as done. should redirect to pt
        ai_url = 'done-action-item'
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(pt.id,)),
                      response.url)
        self.assertTrue(models.ActionItem.objects.all()[0].done())

        # submit a request to reset the ai. should redirect to pt
        ai_url = 'reset-action-item'
        response = self.client.get(reverse(ai_url, args=(ai.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('patient-detail', args=(pt.id,)),
                      response.url)
        self.assertFalse(models.ActionItem.objects.all()[0].done())

    def test_followup_create_urls(self):

        pt = models.Patient.objects.all()[0]

        for fu_type in ["labs", "referral", "general", "vaccine"]:
            url = reverse("new-followup",
                          kwargs={"pt_id": pt.id, 'ftype': fu_type.lower()})

            response = self.client.get(url)
            self.assertEquals(response.status_code, 200)

        url = reverse("followup", kwargs={"pk": pt.id, "model": "Lab"})
