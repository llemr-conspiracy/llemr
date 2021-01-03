import datetime

import factory
from factory.django import DjangoModelFactory
from osler.labs import models
from osler.core.tests import factories as core_factories
from django.utils.timezone import now


class LabTypeFactory(DjangoModelFactory):

	class Meta:
		model = models.LabType

	name = factory.Sequence(lambda n: 'Lab Type #%s' % n)


class ContinuousMeasurementTypeFactory(DjangoModelFactory):
	class Meta:
		model = models.ContinuousMeasurementType

	long_name = factory.Sequence(lambda n: 'Continuous M Type #%s' % n)
	short_name = factory.Sequence(lambda n: 'CMT #%s' % n)
	lab_type = factory.SubFactory(LabTypeFactory)


class DiscreteMeasurementTypeFactory(DjangoModelFactory):
	class Meta:
		model = models.DiscreteMeasurementType

	long_name = factory.Sequence(lambda n: 'Discrete M Type #%s' % n)
	short_name = factory.Sequence(lambda n: 'DMT #%s' % n)
	lab_type = factory.SubFactory(LabTypeFactory)


class DiscreteResultTypeFactory(DjangoModelFactory):
	class Meta:
		model = models.DiscreteResultType

	name = factory.Sequence(lambda n: 'Discrete Result Type #%s' % n)
	is_panic = factory.Iterator(['T', 'F'])


class LabFactory(DjangoModelFactory):
	class Meta:
		model = models.Lab

	patient = factory.SubFactory(core_factories.PatientFactory)
	lab_time = now()
	lab_type = factory.SubFactory(LabTypeFactory)
	encounter = factory.SubFactory(core_factories.EncounterFactory)


class ContinuousMeasurementFactory(DjangoModelFactory):
	class Meta:
		model = models.ContinuousMeasurement

	lab = factory.SubFactory(LabFactory)
	measurement_type = factory.SubFactory(ContinuousMeasurementTypeFactory)
	value = factory.Sequence(lambda n: n)


class DiscreteMeasurementFactory(DjangoModelFactory):
	class Meta:
		model = models.DiscreteMeasurement

	lab = factory.SubFactory(LabFactory)
	measurement_type = factory.SubFactory(DiscreteMeasurementTypeFactory)
	value = factory.SubFactory(DiscreteResultTypeFactory)

