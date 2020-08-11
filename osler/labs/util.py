from .models import *
from itertools import chain
from operator import attrgetter
from django.shortcuts import get_object_or_404


def get_measurements_from_lab(lab_id):
	lab = get_object_or_404(Lab, pk=lab_id)

	cont_list = ContinuousMeasurement.objects.filter(lab=lab)
	disc_list = DiscreteMeasurement.objects.filter(lab=lab)
	measurement_list = sorted(chain(cont_list,disc_list), key=attrgetter('measurement_type'))
	return measurement_list


def get_measurements_from_lab_qs(lab_qs):
	cont_list = ContinuousMeasurement.objects.filter(lab__in=lab_qs)
	disc_list = DiscreteMeasurement.objects.filter(lab__in=lab_qs)
	measurement_list = sorted(chain(cont_list,disc_list), key=attrgetter('measurement_type'))
	return measurement_list


class display_lab_table:
	def __init__(self, dates):
		self.lab_types = list(LabType.objects.all())
		self.measure_types = list(MeasurementType.objects.all())
		self.table_header = ['','Reference'] + dates
		self.table_content = []
		self.sorted_measure_types = []

		for t_lab_type in self.lab_types:
			m_types = self.measure_types.filter(lab_type=t_lab_type)
			#table_1col_header.append('Lab: '+str(t_lab_type))
			self.table_content.append(['Lab: '+str(t_lab_type)])
			for mt in m_types:
				self.table_content[-1].append = [mt, mt.get_ref()] + ['']*len(dates)

	def add_lab(self, lab):
		pass