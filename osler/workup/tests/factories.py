import factory
import factory.fuzzy

from osler.workup import models 
from osler.core.tests import factories as core_factories
import random
import decimal


class WorkupFactory(core_factories.NoteFactory):

	class Meta:
		model = models.Workup

	patient = factory.SubFactory(core_factories.PatientFactory)
	encounter = factory.SubFactory(core_factories.EncounterFactory, patient = factory.SelfAttribute('..patient'))
	chief_complaint = factory.fuzzy.FuzzyChoice(['SOB', 'headache', 'chest pain', 'fatigue'])
	diagnosis = factory.fuzzy.FuzzyChoice(['Influenza', 'MI', 'COPD', 'IBD'])

	@factory.post_generation	
	def diagnosis_categories(self, create, extracted, **kwargs):

		if not create:
			dtype_list = models.DiagnosisType.objects.all()
			dx = random.choice(dtype_list)
			self.diagnosis_categories.add(dx)

		if extracted:
			for dx in extracted:
				self.diagnosis_categories.add(dx)

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
