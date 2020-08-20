from . import models

from itertools import chain
from operator import attrgetter
from django.shortcuts import get_object_or_404


def get_measurements_from_lab(lab_id):
	"""
	Returns a list of measurement objects (both continuous and discrete) that belong to the lab object with given its id
	"""
	lab = get_object_or_404(models.Lab, pk=lab_id)
	cont_list = models.ContinuousMeasurement.objects.filter(lab=lab)
	disc_list = models.DiscreteMeasurement.objects.filter(lab=lab)
	measurement_list = sorted(chain(cont_list,disc_list), key=attrgetter('measurement_type'))
	return measurement_list


def get_measurementtypes_from_labtype(labtype_id):
	"""
	Returns a list of measurement type objects (both continuous and discrete) that belong to the lab type object with given its id
	"""
	labtype = get_object_or_404(models.LabType, pk=labtype_id)
	cont_list = models.ContinuousMeasurementType.objects.filter(lab_type=labtype)
	disc_list = models.DiscreteMeasurementType.objects.filter(lab_type=labtype)
	measurementtype_list = sorted(chain(cont_list,disc_list), key=attrgetter('order_index'))
	return measurementtype_list