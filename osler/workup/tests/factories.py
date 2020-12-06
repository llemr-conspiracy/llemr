import factory
from factory.django import DjangoModelFactory

from osler.workup import models
from osler.core.models import Encounter
from osler.core.tests import factories as core_factory
from django.utils.timezone import now

class ClinicTypeFactory(DjangoModelFactory):

	class Meta:
		model = models.ClinicType

	name = factory.Iterator(["Basic Care Clinic", "Psych Night", "Specialty Night"])


class ClinicDateFactory(DjangoModelFactory):

	class Meta:
		model = models.ClinicDate

	clinic_type = factory.SubFactory(ClinicTypeFactory)
	clinic_date = now()


class EncounterFactory(DjangoModelFactory):

	class Meta:
		model = Encounter

	patient = factory.SubFactory(core_factory.PatientFactory)
	clinic_day = factory.SubFactory(ClinicDateFactory)