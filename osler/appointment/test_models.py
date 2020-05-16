from __future__ import unicode_literals
from builtins import str
from builtins import range
from django.test import TestCase, override_settings
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ValidationError

from osler.core.models import Provider, ProviderType, Patient
from osler.core.tests.test_views import build_provider

from . import models


@override_settings(OSLER_DEFAULT_APPOINTMENT_TIME=(10, 0))
class TestAppointments(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):
        self.all_roles_provider = build_provider()

        self.apt = models.Appointment.objects.create(
            comment='test this stuff',
            clindate=now().date(),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.filter(
                signs_charts=False).first(),
            patient=Patient.objects.first())

    # test editing appointment -- editing should in fact change comment
    def test_edit_appointment(self):
        apt = models.Appointment.objects.first()
        hold_id = apt.id
        apt.comment = "test edit"
        apt.clean()  # unsure if necessary for test
        apt.save()

        self.assertEqual(
            "test edit",
            models.Appointment.objects.filter(id=hold_id).first().comment)
        self.assertEqual(
            now().replace(
                hour=settings.OSLER_DEFAULT_APPOINTMENT_HOUR,
                minute=0,
                second=0,
                microsecond=0).time(),
            apt.clintime)


@override_settings(OSLER_MAX_APPOINTMENTS=3)
class TestMaxAppointments(TestCase):

    fixtures = ['workup', 'core']

    def setUp(self):

        self.all_roles_provider = build_provider()

        for i in range(settings.OSLER_MAX_APPOINTMENTS):
            models.Appointment.objects.create(
                comment=str(i),
                clindate=now().date(),
                author=Provider.objects.first(),
                author_type=ProviderType.objects.filter(signs_charts=False).first(),
                patient=Patient.objects.first())

    # test creation of too many appointments
    def test_creating_past_max_appointment(self):

        # maximum number have already been created
        apt = models.Appointment(
            comment="one more",
            clindate=now().date(),
            author=Provider.objects.first(),
            author_type=ProviderType.objects.filter(signs_charts=False).first(),
            patient=Patient.objects.first())

        with self.assertRaises(ValidationError):
            apt.clean()

    # test editing appointment after max number have been made
    def test_edit_max_appointment(self):
        self.apt = models.Appointment.objects.first()
        hold_id = self.apt.id
        self.apt.comment = "test edit"
        self.apt.clean()
        self.apt.save()
        self.assertEqual("test edit", models.Appointment.objects.filter(id=hold_id).first().comment)
