from __future__ import unicode_literals
import datetime

from django.test import TestCase
from django.urls import reverse

from osler.core.tests.test_views import log_in_provider, build_provider
from osler.core.models import (
    Gender, Patient, Provider, ProviderType)

from . import forms
from . import models


class TestVaccineSeriesCreate(TestCase):
    '''Tests the vaccine series create page'''

    fixtures = ['core']

    def setUp(self):
        log_in_provider(self.client, build_provider())

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
        )

    def test_vaccine_series_create_view(self):
        series1 = models.VaccineSeriesType.objects.create(
            name="Hepatitis A")
        series2 = models.VaccineSeriesType.objects.create(
            name="Influenza")

        url = reverse('new-vaccine-series',
                      args=(self.pt.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, series1.name)
        self.assertContains(response, series2.name)

        response = self.client.post(
            url, {'kind': series1.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.VaccineSeries.objects.count(), 1)

        new_series = models.VaccineSeries.objects.all()[0]
        self.assertRedirects(response,reverse('new-vaccine-dose',
            kwargs={'pt_id': self.pt.id,'series_id': new_series.id}))


class TestVaccineSeriesSelect(TestCase):

    fixtures = ['core']

    def setUp(self):
        log_in_provider(self.client, build_provider())

        self.pt = Patient.objects.create(
            first_name="Juggie",
            last_name="Brodeltein",
            middle_name="Bayer",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1990, 1, 1),
            patient_comfortable_with_english=False,
        )
        self.series_type = models.VaccineSeriesType.objects.create(
            name="Hepatitis A")

    def test_vaccine_series_select_view(self):
        #Create vaccine series for patient
        series1 = models.VaccineSeries.objects.create(
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt,
            kind=self.series_type)

        series2 = models.VaccineSeries.objects.create(
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=self.pt,
            kind=models.VaccineSeriesType.objects.create(name="Flu"))

        #Create vaccine series for another patient
        pt2 = Patient.objects.create(
            first_name="Arthur",
            last_name="Miller",
            middle_name="",
            phone='+49 178 236 5288',
            gender=Gender.objects.first(),
            address='Schulstrasse 9',
            city='Munich',
            state='BA',
            zip_code='63108',
            pcp_preferred_zip='63018',
            date_of_birth=datetime.date(1994, 1, 22),
            patient_comfortable_with_english=False,
        )

        series3 = models.VaccineSeries.objects.create(
            author=Provider.objects.first(),
            author_type=ProviderType.objects.first(),
            patient=pt2,
            kind=models.VaccineSeriesType.objects.create(name="MMR"))

        #Two vaccine series for patient 1
        url = reverse('select-vaccine-series',
                      args=(self.pt.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, series1)
        self.assertContains(response, series2)
        self.assertNotContains(response, series3)

        #Contains the button to make new series
        self.assertContains(
            response,
            '<a href="%s">Create new vaccine series</a>' %
            reverse('new-vaccine-series', args=(self.pt.id,)))

        #One vaccine series for patient 2
        url = reverse('select-vaccine-series',
                      args=(pt2.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, series1)
        self.assertNotContains(response, series2)
        self.assertContains(response, series3)

        #Submit form and redirect correctly
        response = self.client.post(
            reverse('select-vaccine-series', args=(pt2.id,)),
            {'series': series3.pk})
        self.assertRedirects(response,reverse('new-vaccine-dose',
            kwargs={'pt_id': pt2.id,'series_id': series3.id}))


# class TestVaccineDoseCreate(TestCase):
#   def setUp(self):
#         log_in_provider(self.client, build_provider())

#         self.pt = Patient.objects.create(
#             first_name="Juggie",
#             last_name="Brodeltein",
#             middle_name="Bayer",
#             phone='+49 178 236 5288',
#             gender=Gender.objects.first(),
#             address='Schulstrasse 9',
#             city='Munich',
#             state='BA',
#             zip_code='63108',
#             pcp_preferred_zip='63018',
#             date_of_birth=datetime.date(1990, 1, 1),
#             patient_comfortable_with_english=False,
#         )
#         self.series_type = models.VaccineSeriesType.objects.create(
#           name="Hepatitis A")
#         self.series = models.VaccineSeries.objects.create(
#           author=Provider.objects.first(),
#           author_type=ProviderType.objects.first(),
#           patient=self.pt,
#           kind=self.series_type)

#     def test_vaccine_dose_create_view(self):
#       dosetype1 = models.VaccineDoseType.objects.create(
#           kind=self.series_type,
#           time_from_first=datetime.timedelta(0))
#       dosetype2 = models.VaccineDoseType.objects.create(
#           kind=self.series_type,
#           time_from_first=datetime.timedelta(days=30))

#       #Create another series type and subsequent dose type
#       series_type2 = models.VaccineSeriesType.objects.create(
#           name="Flu")
#       dosetype3 = models.VaccineDoseType.objects.create(
#           kind=series_type2,
#           time_from_first=datetime.timedelta(0))

#       url = reverse('new-vaccine-dose',
#           kwargs={'pt_id': self.pt.id,'series_id': self.series.id})
#       response = self.client.get(url)

#       #Two dose types for this series type
#       self.assertEqual(response.status_code, 200)
#         self.assertContains(response, dosetype1)
#         self.assertContains(response, dosetype2)
#         self.assertNotContains(response, dosetype3)

#         #Submit form for first dose, redirect to action item

#         #Submit form for last dose, redirect to patient detail
        

