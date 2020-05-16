from __future__ import unicode_literals
from django.test import TestCase
from django.utils.timezone import now
from osler.core.models import Provider, ProviderType, Patient
from datetime import time
from .forms import AppointmentForm


def apt_dict():
    apt = {'clindate': now().date(),
           'clintime': time(9, 0),
           'appointment_type': 'PSYCH_NIGHT',
           'comment': 'stuff',
           'author': Provider.objects.first(),
           'author_type': ProviderType.objects.first(),
           'patient': Patient.objects.first().id}

    return(apt)


class TestAppointmentForm(TestCase):

    fixtures = ['core.json']

    def setUp(self):
        apt = apt_dict()
        self.apt = apt

        form = AppointmentForm(data=apt)
        self.assertTrue(form.is_valid(), msg=form.errors)

    # create appointment fails if Patient name is unspecified
    def test_appointment_no_patient_error(self):
        apt = self.apt.copy()
        apt['patient'] = None
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)
        del(apt['patient'])
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)

    # create appointment fails if Appointment Date is unspecified
    def test_appointment_no_date_error(self):
        apt = self.apt.copy()
        apt['clindate'] = None
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)

    # create appointment fails if time of appointment is unspecified
    def test_appointment_no_time_error(self):
        apt = self.apt.copy()
        apt['clintime'] = None
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)

    # create appointment fails if Appointment Type is unspecified
    def test_appointment_no_type_error(self):
        apt = self.apt.copy()

        apt['appointment_type'] = 'self care'
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)

        # create appointment also fails if type is not one of the 3 options
        apt['appointment_type'] = None
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)

    # create appointment fails if Comment is unspecified or ''
    def test_appointment_no_comment_error(self):
        apt = self.apt.copy()

        apt['comment'] = ''
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)

        apt['comment'] = None
        form = AppointmentForm(data=apt)
        self.assertFalse(form.is_valid(), msg=form.errors)
