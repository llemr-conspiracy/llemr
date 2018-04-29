from django.db import models

from pttrack.models import Note
# from workup.models import ClinicDate
from simple_history.models import HistoricalRecords


class Appointment(Note):

	clindate = models.DateField(verbose_name="Appointment Date")
	comment = models.TextField(
		help_text="What should happen at this appointment?")
	history = HistoricalRecords()
