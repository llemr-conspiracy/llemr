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
