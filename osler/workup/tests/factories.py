import factory
from factory.django import DjangoModelFactory

from osler.workup import models
from osler.core.tests import factories as core_factories
from osler.users.tests import factories as user_factories


class WorkupFactory(DjangoModelFactory):

	class Meta:
		model = models.Workup

	encounter = factory.SubFactory(core_factories.EncounterFactory)
	patient = factory.SubFactory(core_factories.PatientFactory)
	chief_complaint = 'SOB'
	diagnosis = 'MI'
	hpi = 'hard to breathe'
	pmh = 'none'
	psh = 'none'
	meds = 'none'
	allergies = 'none'
	fam_hx = 'none'
	soc_hx = 'none'
	ros = 'none'
	pe = 'CTAB'
	a_and_p = 'stop'
	hr = 90
	bp_sys = 120
	bp_dia = 80
	rr = 16
	t = 98
	labs_ordered_internal = 'none'
	labs_ordered_external = 'none'
	got_voucher = False
	got_imaging_voucher = False