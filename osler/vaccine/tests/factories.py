import datetime

import factory
from factory.django import DjangoModelFactory
from osler.vaccine import models
from osler.core.tests import factories as core_factories


class VaccineSeriesTypeFactory(DjangoModelFactory):

    class Meta:
        model = models.VaccineSeriesType

    name = factory.Iterator(["Flu", "Hep A", "Polio", "Coronavirus"])


class VaccineDoseTypeFactory(DjangoModelFactory):
    class Meta:
        model = models.VaccineDoseType

    kind = factory.SubFactory(VaccineSeriesTypeFactory)


class VaccineSeriesFactory(DjangoModelFactory):

	class Meta:
		model = models.VaccineSeries

	kind = factory.SubFactory(VaccineSeriesTypeFactory)
	patient = factory.SubFactory(core_factories.PatientFactory)


class VaccineDoseFactory(DjangoModelFactory):

	class Meta:
		model = models.VaccineDose

	series = factory.SubFactory(VaccineSeriesFactory)
	which_dose = factory.SubFactory(VaccineDoseTypeFactory)
	patient = factory.SubFactory(core_factories.PatientFactory)
	encounter = factory.SubFactory(core_factories.EncounterFactory)



