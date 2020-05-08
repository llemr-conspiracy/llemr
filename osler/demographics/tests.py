from __future__ import unicode_literals
from datetime import date

from django.test import TestCase
from django.urls import reverse

from pttrack.test_views import build_provider, log_in_provider
from pttrack.models import Patient, Gender, ContactMethod

from . import models
from . import forms


class ViewsExistTest(TestCase):
    '''
    Verify that views involving the wokrup are functioning.
    '''
    fixtures = ['pttrack']

    def setUp(self):

        log_in_provider(self.client, build_provider())

        models.IncomeRange.objects.create(name="Default")
        models.EducationLevel.objects.create(name="Default")
        models.WorkStatus.objects.create(name="Default")
        models.ResourceAccess.objects.create(name="Default")
        models.ChronicCondition.objects.create(name="Default")
        models.TransportationOption.objects.create(name="Default")

    def test_url_response(self):

        dg_urls = ['demographics-detail', 'demographics-update']

        dg = models.Demographics.objects.create(
            creation_date=date.today(),
            annual_income=models.IncomeRange.objects.all()[0],
            education_level=models.EducationLevel.objects.all()[0],
            transportation=models.TransportationOption.objects.all()[0],
            work_status=models.WorkStatus.objects.all()[0],
            has_insurance=True,
            ER_visit_last_year=True,
            last_date_physician_visit=date.today(),
            lives_alone=True,
            dependents=4,
            currently_employed=True)

        dg.chronic_condition.add(models.ChronicCondition.objects.all()[0])
        dg.resource_access.add(models.ResourceAccess.objects.all()[0])
        dg.save()

        pt = Patient.objects.all()[0]
        pt.demographics = dg
        pt.save()

        dg.patient = pt
        dg.save()

        for dg_url in dg_urls:
            response = self.client.get(reverse(dg_url, args=(dg.id,)))
            self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('demographics-create', args=(pt.id,)))
        self.assertEqual(response.status_code, 200)


class FormSubmissionTest(TestCase):
    '''
    Verify that views involving the wokrup are functioning.
    '''
    fixtures = ['pttrack']

    def setUp(self):

        log_in_provider(self.client, build_provider())

        models.IncomeRange.objects.create(name="Default")
        models.EducationLevel.objects.create(name="Default")
        models.WorkStatus.objects.create(name="Default")
        models.ResourceAccess.objects.create(name="Default")
        models.ChronicCondition.objects.create(name="Default")
        models.TransportationOption.objects.create(name="Default")

    def make_patient(self):
        return models.Patient.objects.create(
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
            date_of_birth=date(1990, 1, 1),
            patient_comfortable_with_english=False,
            preferred_contact_method=ContactMethod.objects.all()[0])

    def test_demographics_form_submission(self):
        '''
        Test submission of a demographics form
        '''

        for i in [True, False, None]:

            pt = self.make_patient()

            valid_dg_dict = {
                'creation_date': date.today(),
                'annual_income': models.IncomeRange.objects.all()[0],
                'education_level': models.EducationLevel.objects.all()[0],
                'transportation': models.TransportationOption.objects.all()[0],
                'work_status': models.WorkStatus.objects.all()[0],
                'last_date_physician_visit': date.today(),
                'dependents': 4,
            }

            if i is True or i is False:
                valid_dg_dict['has_insurance'] = i
                valid_dg_dict['ER_visit_last_year'] = i
                valid_dg_dict['lives_alone'] = i
                valid_dg_dict['currently_employed'] = i

            final_url = reverse('demographics-create', args=(pt.id,))

            form = forms.DemographicsForm(data=valid_dg_dict)
            self.assertTrue(form.is_valid())

            dg_number = len(models.Demographics.objects.all())
            response = self.client.get(final_url)
            response = self.client.post(final_url, valid_dg_dict)

            self.assertEqual(response.status_code, 302)
            self.assertEquals(len(models.Demographics.objects.all()),
                              dg_number + 1)

            dg = models.Demographics.objects.last()

            self.assertEquals(dg.has_insurance, i)
            self.assertEquals(dg.ER_visit_last_year, i)
            self.assertEquals(dg.lives_alone, i)
            self.assertEquals(dg.currently_employed, i)

            final_url = reverse('demographics-update', args=(dg.pk,))
            response = self.client.get(final_url)
            response = self.client.post(final_url, valid_dg_dict)

            self.assertEqual(response.status_code, 302)

    def test_demographics_form_double_submission(self):
        '''Test two submissions of the form to avoid duplicate entry errors
        '''

        pt = self.make_patient()

        # Need to create dictionary to submit a POST request
        dg = {
            'patient': pt,
            'creation_date': date.today(),
            'annual_income': models.IncomeRange.objects.all()[0],
            'education_level': models.EducationLevel.objects.all()[0],
            'transportation': models.TransportationOption.objects.all()[0],
            'work_status': models.WorkStatus.objects.all()[0],
            'ER_visit_last_year': True,
            'last_date_physician_visit': date.today(),
            'lives_alone': False,
            'dependents': 4,
        }

        # Submit demographics object twice
        dg_url = reverse('demographics-create', args=(pt.pk,))
        response = self.client.post(dg_url, dg, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'pttrack/patient_detail.html')
        self.assertEqual(models.Demographics.objects.count(), 1)

        # Send in submission with the same patient ID; we should see no new
        # Demographics objects, and a successful redirect to patient-detail
        response2 = self.client.post(dg_url, dg, follow=True)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(models.Demographics.objects.count(), 1)
        self.assertTemplateUsed(
            response2, 'pttrack/patient_detail.html')

    def test_demographics_form_double_submission_errors(self):
        '''
        Tests the error messages displayed in the double submission form
        '''

        # Test case 1 - same form submitted twice, no error messages should up
        pt = self.make_patient()
        dg = {
            'patient': pt,
            'creation_date': date.today(),
            'annual_income': models.IncomeRange.objects.first(),
            'education_level': models.EducationLevel.objects.first(),
            'transportation': models.TransportationOption.objects.first(),
            'work_status': models.WorkStatus.objects.first(),
            'ER_visit_last_year': True,
            'last_date_physician_visit': date.today(),
            'lives_alone': False,
            'dependents': 4,
        }

        dg_url = reverse('demographics-create', args=(pt.pk,))

        response1 = self.client.post(dg_url, dg, follow=True)
        self.assertTemplateUsed(response1, 'pttrack/patient_detail.html')

        response2 = self.client.post(dg_url, dg, follow=True)
        #  success here means redirection to patient detail page
        self.assertNotContains(response2, 'Clash')
        self.assertTemplateUsed(response2, 'pttrack/patient_detail.html')

        # Test case 2 - two different forms submitted
        # In this case, all fields should have errors
        # 3 errors introduced in has_insurane, ER_visit_last_year,
        # and dependents
        dg2 = {
            'patient': pt,
            'creation_date': date.today(),
            'annual_income': models.IncomeRange.objects.first(),
            'education_level': models.EducationLevel.objects.first(),
            'transportation': models.TransportationOption.objects.first(),
            'work_status': models.WorkStatus.objects.first(),
            'has_insurance': True,
            'ER_visit_last_year': False,
            'last_date_physician_visit': date.today(),
            'lives_alone': False,
            'dependents': 6,
        }

        response3 = self.client.post(dg_url, dg2, follow=True)

        self.assertFormError(
            response3, 'form_old', 'has_insurance',
            "Clash in this field. Database entry is 'None'")
        self.assertFormError(
            response3, 'form_new', 'ER_visit_last_year',
            "Clash in this field. You entered 'False'")
        self.assertFormError(
            response3, 'form_old', 'dependents',
            "Clash in this field. Database entry is '4'")
        self.assertFormError(
            response3, 'form_new', 'dependents',
            "Clash in this field. You entered '6'")

        # Verify that there are 6 errors on page (3 fields x 2 messages)
        self.assertContains(response3, 'Clash', count=6)
