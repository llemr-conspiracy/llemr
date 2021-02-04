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
	#diagnosis is a multiple choice foreign key to the DiagnosisType model
	diagnosis = factory.Iterator(["Influenza", "MI", "COPD", "Ulcer"])
	diagnosis_categories = factory.SubFactory(DiagnosisTypeFactory)
	#ok so justin said he wanted a multiple foreign key, but this is me copying the format of languages in the factories.py in core
	#which seems like relatively the same scenario... seems wrong though because it doesn't mention manytomany or foreign key
	#but neither does the core factory
	#or do i want it to be many to many!!!!!!
	#should probably ask just not 100% sure about this foreign key here... but must move forward!
	#PROBLEM: wanted the models from the django database but instead we are using models from workup?
	#diagnosis = factory.Iterator(["MI", "Influenza", "COPD", "Ulcer"])
	# want this to be a multiple choice foreign key to the diagnosis type model...
	#factory faker to look at documentation online
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

