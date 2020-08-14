from . import models

from itertools import chain
from operator import attrgetter
from django.shortcuts import get_object_or_404


# TODO add doc string

def get_measurements_from_lab(lab_id):

	lab = get_object_or_404(models.Lab, pk=lab_id)
	cont_list = models.ContinuousMeasurement.objects.filter(lab=lab)
	disc_list = models.DiscreteMeasurement.objects.filter(lab=lab)
	measurement_list = sorted(chain(cont_list,disc_list), key=attrgetter('measurement_type'))
	return measurement_list

