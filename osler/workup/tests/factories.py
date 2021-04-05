import factory
from factory.django import DjangoModelFactory
from faker import Faker

import factory.fuzzy



from osler.workup import models 
from osler.core import models as core_models
from osler.core.tests import factories as core_factories
from osler.users.tests import factories as user_factories

fixtures = ['workup']
import random
import decimal


class WorkupFactory(core_factories.NoteFactory):
	#just for testing
	#note = factory.SubFactory(core_factories.NoteFactory)

	class Meta:
		model = models.Workup

	#fixtures = ['workup']
	
	patient = factory.SubFactory(core_factories.PatientFactory)
	encounter = factory.SubFactory(core_factories.EncounterFactory, patient = factory.SelfAttribute('..patient'))
	chief_complaint = factory.fuzzy.FuzzyChoice(['SOB', 'headache', 'chest pain', 'fatigue'])
	print("error here")
	#chief_complaint = factory.Iterator(["SOB", "Headache", "Chest pain", "Fatigue"])
	#diagnosis = factory.SubFactory(DiagnosisFactory)
	diagnosis = factory.fuzzy.FuzzyChoice(['Influenza', 'MI', 'COPD', 'IBD'])

	
	@factory.post_generation	
	def diagnosistype(self, create, extracted, **kwargs):
		#if not create:
		dtype_list = models.DiagnosisType.objects.all()
		#import pdb
		#pdb.set_trace()
		diagnosis_type = random.choice(dtype_list)
		self.diagnosis_categories.add(diagnosis_type)

		#if extracted:
			#for diagnosistype in extracted:
				#self.diagnosistype.add(diagnosistype)
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

	
	height = random.randint(48,72)

	weight = random.randint(80,550)


	voucher_amount = random.randint(100,2000)
	patient_pays = random.randint(0,200)

	imaging_voucher_amount = random.randint(100,2000)
	patient_pays_imaging = random.randint(0,200)



	
	

