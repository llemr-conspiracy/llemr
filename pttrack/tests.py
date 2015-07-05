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
                   'followup-choice']
        pt = models.Patient.objects.all()[0]

        for pt_url in pt_urls:
            response = self.client.get(reverse(pt_url, args=(pt.id,)))
            self.assertEqual(response.status_code, 200)

        pt_url = 'new-workup'
        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('new-clindate', args=(pt.id,)), response.url)

        models.ClinicDate.objects.create(
            clinic_type=models.ClinicType.objects.all()[0],
            clinic_date=datetime.datetime.today(),
            gcal_id="tmp")

        response = self.client.get(reverse(pt_url, args=(pt.id,)))
        self.assertEqual(response.status_code, 200)


    def test_workup_urls(self):
        wu_urls = ['workup',
                   'workup-update',
                   'workup-sign']

        # for wu_url in wu_urls:
        #     response = self.client.get(reverse(wu_url, args=(wu.id,)))
        #     assertEqual(response.status_code, 200)

        # if there's no clindate, this will redirect.



    def test_action_item_urls(self):
        ai_urls = ['done-action-item',
                   'reset-action-item']

        # for ai_url in ai_urls:
        #     response = self.client.get(reverse(ai_url, args=(ai.id,)))
        #     assertEqual(response.status_code, 200)

    def test_followup_urls(self):
        fu_url = 'followup'

        pt = models.Patient.objects.all()[0]

        # for fu_type in ['Lab', 'Vaccine', 'General', 'Referral']:
        #     response = self.client.get(reverse(fu_url, args=(pt.id, fu_type)))
        #     assertEqual(response.status_code, 200)
