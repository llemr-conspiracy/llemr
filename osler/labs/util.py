from .models import *
from itertools import chain
from operator import attrgetter
from django.shortcuts import get_object_or_404
from django.utils import timezone

from django.contrib.auth.models import Permission, Group
from django.core.exceptions import PermissionDenied


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


# Return permissions associated with the user's current group and 
# the user specifically
def get_current_permission(request_user):
	active_role = request_user.active_role
	assert request_user.groups.filter(pk=active_role.pk).exists()
	current_group = get_object_or_404(request_user.groups,pk=active_role.pk)
	group_permissions = Permission.objects.filter(group=current_group)
	user_permissions = Permission.objects.filter(user=request_user)
	return (group_permissions | user_permissions)


# Returns a function that can be passed on to @user_passes_test
# Test if the user (signed in to current group) has the given perm
def generate_has_perm_func(perm_name, raise_exception=False):
	APP_LABEL = 'labs'
	given_perm = get_object_or_404(Permission, codename=perm_name, content_type__app_label=APP_LABEL)
	def helper_func(request_user):
		current_perm_qs = get_current_permission(request_user)
		has_perm = given_perm in current_perm_qs
		if (not has_perm) and raise_exception:
			raise PermissionDenied
		return has_perm
	return helper_func


# Test if the user (signed in to current group) has the given perm
def has_perm_for_labs(request_user, perm_name):
	APP_LABEL = 'labs'
	given_perm = get_object_or_404(Permission, codename=perm_name, content_type__app_label=APP_LABEL)
	current_perm_qs = get_current_permission(request_user)
	has_perm = given_perm in current_perm_qs
	return has_perm


