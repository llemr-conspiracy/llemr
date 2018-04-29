from .forms import AppointmentForm

from django.test import TestCase


class TestAppointmentForm(TestCase):

	fixtures = ['pttrack.json']

	def test_appointmentform(self):
		# Create a form and then test if clinic date has been created
		

