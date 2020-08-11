from __future__ import unicode_literals
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from osler.vaccine import models, forms
from osler.core.models import (
    Gender, Patient, ActionInstruction)
from osler.followup.models import (ContactMethod, ContactResult)

from osler.core.tests.test_views import log_in_user, build_user
from osler.core.tests import factories as core_factories
from osler.users.tests import factories as user_factories
from osler.vaccine.tests import factories


class TestVaccineSeriesCreate(TestCase):
    '''Tests the vaccine series create page'''

    fixtures = ['core']

    def setUp(self):
        log_in_user(self.client, build_user())

        self.pt = core_factories.PatientFactory(
            case_managers=self.user)

    def test_vaccine_series_create_view(self):
        series1 = factories.VaccineSeriesTypeFactory()
        series2 = factories.VaccineSeriesTypeFactory()

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
        self.user = build_user()

        log_in_user(self.client, self.user)

        self.pt = core_factories.PatientFactory(
            case_managers=self.user)

        self.series_type = factories.VaccineSeriesTypeFactory()

    def test_vaccine_series_select_view(self):
        #Create vaccine series for patient
        series1 = factories.VaccineSeriesFactory(
            author=self.user,
            author_type=self.user.groups.first(),
            patient=self.pt,
            kind=self.series_type)

        series2 = models.VaccineSeries.objects.create(
            author=self.user,
            author_type=self.user.groups.first(),
            patient=self.pt,
            kind=factories.VaccineSeriesTypeFactory())

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
            author=self.user,
            author_type=self.user.groups.first(),
            patient=pt2,
            kind=factories.VaccineSeriesTypeFactory())

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
        response = self.client.post(url,
            {'series': series3.pk})
        self.assertRedirects(response,reverse('new-vaccine-dose',
            kwargs={'pt_id': pt2.id,'series_id': series3.id}))


class TestVaccineDoseCreate(TestCase):

    fixtures = ['core']

    def setUp(self):
        self.user = build_user()

        log_in_user(self.client, self.user)

        self.pt = core_factories.PatientFactory(
            case_managers=self.user)

        self.series_type = factories.VaccineSeriesTypeFactory()

        self.series = factories.VaccineSeriesFactory(
            author=self.user,
            author_type=self.user.groups.first(),
            patient=self.pt,
            kind=self.series_type)

    def test_vaccine_dose_create_view(self):
        dosetype1 = factories.VaccineDoseTypeFactory(
            kind=self.series_type,
            time_from_first=datetime.timedelta(0))
        dosetype2 = factories.VaccineDoseTypeFactory(
            kind=self.series_type,
            time_from_first=datetime.timedelta(days=30))

        #Create another series type and subsequent dose type
        series_type2 = factories.VaccineSeriesTypeFactory()
        dosetype3 = models.VaccineDoseType.objects.create(
            kind=series_type2,
            time_from_first=datetime.timedelta(0))

        url = reverse('new-vaccine-dose',
            kwargs={'pt_id': self.pt.id,'series_id': self.series.id})
        response = self.client.get(url)

        #Two dose types for this series type
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, dosetype1)
        self.assertContains(response, dosetype2)
        self.assertNotContains(response, dosetype3)

        #Submit form for last dose, redirect to patient detail
        response = self.client.post(url,
            {'which_dose': dosetype2.pk})
        self.assertRedirects(response,
            reverse('core:patient-detail',args=(self.pt.id,)))

        #Submit form for first dose, redirect to action item with correct due date url
        response = self.client.post(url,
            {'which_dose': dosetype1.pk})

        new_dose = models.VaccineDose.objects.all()[0]
        formatted_date = new_dose.next_due_date().strftime("%D")
        querystr = '%s=%s' % ("due_date", formatted_date)
        new_url = "%s?%s" % (reverse('new-vaccine-ai', 
            kwargs={'pt_id': self.pt.id, 'series_id': self.series.id}), querystr)
        
        self.assertRedirects(response,new_url)


class TestVaccineActionItemCreate(TestCase):

    fixtures = ['core']

    def setUp(self):
        self.user = build_user()

        log_in_user(self.client, self.user)

        self.pt = core_factories.PatientFactory(
            case_managers=self.user)

        self.series_type = factories.VaccineSeriesTypeFactory()

        self.series = factories.VaccineSeriesFactory(
            author=self.user,
            author_type=self.user.groups.first(),
            patient=self.pt,
            kind=self.series_type)

    def test_vaccine_ai_create(self):

        self.assertEqual(models.VaccineActionItem.objects.count(), 0)

        url = reverse('new-vaccine-ai', kwargs={'pt_id': self.pt.id, 'series_id': self.series.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        submitted_ai = {
            "instruction": ActionInstruction.objects.create(instruction="Call"),
            "due_date": str(datetime.date.today()),
            "comments": "an arbitrary string comment"
        }

        response = self.client.post(url, submitted_ai)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:patient-detail', args=(self.pt.id,)))
        self.assertEqual(models.VaccineActionItem.objects.count(), 1)

    def test_vaccine_ai_mark_done_url(self):

        vai = models.VaccineActionItem.objects.create(
            instruction=ActionInstruction.objects.create(instruction="Please call"),
            due_date=datetime.date.today(),
            comments="",
            author=self.user,
            author_type=self.user.groups.first(),
            patient=self.pt,
            vaccine=self.series)

        #vmark_done_url on patient detail
        response = self.client.get(
            reverse('core:patient-detail', args=(self.pt.id,)))
        self.assertContains(response, vai.mark_done_url())

        #vaccine ai is not done yet
        self.assertEqual(vai.done(), False)


class TestVaccineFollowupCreate(TestCase):

    fixtures = ['core']

    def setUp(self):
        self.user = build_user()

        log_in_user(self.client, self.user)

        self.pt = core_factories.PatientFactory(
            case_managers=self.user)

        self.series_type = factories.VaccineSeriesTypeFactory()

        self.series = factories.VaccineSeriesFactory(
            author=self.user,
            author_type=self.user.groups.first(),
            patient=self.pt,
            kind=self.series_type)

        self.vai = models.VaccineActionItem.objects.create(
            instruction=ActionInstruction.objects.create(instruction="Please call"),
            due_date=datetime.date.today(),
            comments="",
            author=self.user,
            author_type=self.user.groups.first(),
            patient=self.pt,
            vaccine=self.series)

    def test_vaccine_fu_create(self):

        url = reverse('new-vaccine-followup',
            kwargs={'pt_id':self.pt.id,'ai_id':self.vai.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        contact_method = ContactMethod.objects.create(name="Ritual")
        contact_resolution = ContactResult.objects.create(name="Eureka")

        for button_clicked in ['followup_create', 'followup_close']:
            submitted_fu = {
                "contact_method": contact_method,
                "contact_resolution": contact_resolution,
                "comments": "",
                "action_item": self.vai,
                button_clicked: True}

            response = self.client.post(url,submitted_fu)
            self.assertEqual(response.status_code, 302)

            #Action Item marked done after subsmission
            vai = models.VaccineActionItem.objects.first()
            self.assertEqual(vai.completion_date.date(), now().date())

            if 'followup_create' in submitted_fu:
                self.assertRedirects(response,reverse('new-vaccine-ai', 
                    kwargs={'pt_id': self.pt.id, 'series_id': self.series.id}))
            elif 'followup_close' in submitted_fu:
                self.assertRedirects(response,reverse('core:patient-detail', 
                    args=(self.pt.id,)))
