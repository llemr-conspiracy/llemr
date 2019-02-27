import re
from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from pttrack.models import Provider, ProviderType, Patient
from pttrack.test_views import log_in_provider, build_provider
from datetime import time
from .test_forms import apt_dict

from . import models


class TestAppointmentViews(TestCase):

    fixtures = ['pttrack', 'workup']

    def setUp(self):

        self.all_roles_provider = build_provider()

        log_in_provider(self.client, self.all_roles_provider)

        self.apt = models.Appointment.objects.create(
            comment='test this stuff',
            clindate=now().date(),
            clintime=time(9, 0),
            appointment_type='PSYCH_NIGHT',
            author=Provider.objects.first(),
            author_type=ProviderType.objects.filter(signs_charts=False).first(),
            patient=Patient.objects.first())

    def test_new_appointment_view(self):
        # Getting to new appointment view
        response = self.client.get(reverse("appointment-new"))
        self.assertEqual(response.status_code, 200)

        # Posting new appointment
        response = self.client.post(reverse("appointment-new"), data=apt_dict())
        self.assertEqual(response.status_code, 302)

    def test_update_appointment_view(self):
        apt = models.Appointment.objects.first()

        # Getting to appointment update view
        response = self.client.get(reverse("appointment-update",
                                   kwargs={'pk': apt.pk}))
        self.assertEqual(response.status_code, 200)

        # Posting updated appointment
        self.assertEqual(apt.comment, 'test this stuff')
        response = self.client.post(reverse('appointment-update',
                                    kwargs={'pk': apt.pk}), data=apt_dict())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('appointment-list'))
        apt_test = models.Appointment.objects.filter(id=apt.pk).first()
        self.assertEqual(apt_test.comment, 'stuff')

    def test_new_appointment_with_patient_name(self):
        response = self.client.get("%s?pt_id=%s" %
                                   (reverse("appointment-new"), Patient.objects.filter(pk=1).first().pk))
        self.assertEqual(response.context['form'].initial['patient'],
                         Patient.objects.filter(pk=1).first())

    def test_new_appointment_with_date(self):
        response = self.client.get("%s?date=%s" %
                                   (reverse("appointment-new"), now().date()))
        self.assertEqual(response.context['form'].initial['clindate'],
                         now().date().strftime("%Y-%m-%d"))

    def test_mark_noshow(self):
        self.assertEqual(self.apt.pt_showed, None)
        self.assertEqual(models.Appointment.objects.count(), 1)

        response = self.client.get(reverse("appointment-mark-no-show",
                                           args=(self.apt.pk,)))

        self.assertRedirects(response, reverse('appointment-list'))

        self.assertEqual(models.Appointment.objects.count(), 1)
        self.assertEqual(models.Appointment.objects.first().pt_showed, False)

        response = self.client.get('appointment-list')
        # one 'mark as noshow' link should be gone now
        noshow_links = re.findall(
            re.escape('href="/appointment/') +
            r'[0-9]+' +
            re.escape('/noshow'),
            response.content)
        self.assertEqual(len(noshow_links), 0)

    def test_mark_arrived(self):
        self.assertEqual(self.apt.pt_showed, None)
        self.assertEqual(models.Appointment.objects.count(), 1)

        response = self.client.get(reverse("appointment-mark-arrived",
                                           args=(self.apt.pk,)))
        self.assertRedirects(response, reverse('appointment-list'))

        self.assertEqual(models.Appointment.objects.count(), 1)
        self.assertEqual(models.Appointment.objects.first().pt_showed, True)

        response = self.client.get('appointment-list')
        # one 'mark as arrived' link should be gone now
        arrived_links = re.findall(
            re.escape('href="/appointment/') +
            r'[0-9]+' +
            re.escape('/arrived'),
            response.content)

        self.assertEqual(len(arrived_links), 0)

    def test_first_apt_is_today(self):

        apts = []
        for datedelta in [-1, 1]:
            date = now().date() - timedelta(days=datedelta)

            apts.append(models.Appointment.objects.create(
                comment='test this stuff',
                clindate=date,
                clintime=time(9, 0),
                appointment_type='PSYCH_NIGHT',
                author=Provider.objects.first(),
                author_type=ProviderType.objects.filter(
                    signs_charts=False).first(),
                patient=Patient.objects.first()))

        # three appointments should exist, total
        self.assertEqual(models.Appointment.objects.count(), 3)

        response = self.client.get(reverse("appointment-list"), follow=True)
        self.assertTemplateUsed('appointment/appointment_list.html')

        with open('tmp.html', 'w') as f:
            f.write(response.content)

        # only two panels should appear, since one apt is in the past and
        # two fall on the same day (today)
        for i in range(2):
            self.assertContains(
                response, 'appointment-panel-%s' % i)
            self.assertContains(
                response, 'appointment-table-%s' % i)

        # only one new appointment link should appear, since the "today"
        # panel shouldn't get one
        new_appointment_links = re.findall(
            re.escape('href="/appointment/new?date=') +
            r'[0-9]{4}-[0-9]{2}-[0-9]{2}',
            response.content)

        self.assertEqual(len(new_appointment_links), 1)

        # one 'mark as noshow' link should appear, since the the today
        # panel has two pts
        noshow_links = re.findall(
            re.escape('href="/appointment/') +
            r'[0-9]+' +
            re.escape('/noshow'),
            response.content)

        self.assertEqual(len(noshow_links), 1)

        # one 'mark as here' link should appear, since the the today
        # panel has two pts
        arrived_links = re.findall(
            re.escape('href="/appointment/') +
            r'[0-9]+' +
            re.escape('/arrived'),
            response.content)

        self.assertEqual(len(arrived_links), 1)

