import factory
from factory.django import DjangoModelFactory


from osler.workup import models 
from osler.core.tests import factories as core_factories
from osler.users.tests import factories as user_factories

import random
import decimal


class DiagnosisTypeFactory(DjangoModelFactory):

    class Meta:
        model = models.DiagnosisType

    name = factory.Iterator("Cardiovascular","Respiratory", "GI")


class WorkupFactory(DjangoModelFactory):

	class Meta:
		model = models.Workup

	encounter = factory.SubFactory(core_factories.EncounterFactory)
	patient = factory.SubFactory(core_factories.PatientFactory)
	chief_complaint = factory.Iterator(["SOB", "Headache", "Chest pain", "Fatigue"])
	diagnosis = factory.Iterator(["Influenza", "MI", "COPD", "Ulcer"])
	diagnosis_categories = factory.SubFactory(DiagnosisTypeFactory)
	hpi = factory.Faker('paragraph')
	pmh = factory.Faker('paragraph')
	psh = factory.Faker('paragraph')
	meds = factory.Faker('paragraph')
	allergies = factory.Faker('paragraph')
	fam_hx = factory.Faker('paragraph')
	soc_hx = factory.Faker('paragraph')
	ros = factory.Faker('paragraph')
	pe = factory.Faker('paragraph')
	a_and_p = factory.Faker('paragraph')
	hr = random.randint(60,100)
	bp_sys = random.randint(90,120)
	bp_dia = random.randint(60,80)
	rr = random.randint(12,40)
	t = float(decimal.Decimal(random.randrange(960, 1000))/10)
	labs_ordered_internal = factory.Faker('paragraph')
	labs_ordered_external = factory.Faker('paragraph')
	got_voucher = factory.Faker('pybool')
	got_imaging_voucher = factory.Faker('pybool')

