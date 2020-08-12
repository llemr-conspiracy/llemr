from functools import reduce
from osler.core.models import (Patient)
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib.auth.models import Permission, Group

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import *
from .forms import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML, Field
from crispy_forms.bootstrap import (
	InlineCheckboxes, AppendedText, PrependedText)
from django.http import HttpResponseRedirect

from django.utils import timezone
from datetime import datetime, timedelta

from itertools import chain
from operator import attrgetter

from .util import *

class LabListView(ListView):
	model = Lab
	template_name = 'labs/lab_all.html'
	context_object_name = 'labs'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		self.pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
		context['pt'] = self.pt
		context['labs'] = Lab.objects.filter(patient=self.kwargs['pt_id'])
		has_add_perm = has_perm_for_labs(self.request.user, 'add_lab')
		context['add_perm'] = has_add_perm
		return context


class LabDetailView(DetailView):
	model = Lab
	context_object_name = 'lab'

	def get_context_data(self, **kwargs):
		context = super(LabDetailView,self).get_context_data(**kwargs)
		self.lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
		context['lab'] = self.lab
		context['pt'] = self.lab.patient
		#cont_list = ContinuousMeasurement.objects.filter(lab=self.lab)
		#disc_list = DiscreteMeasurement.objects.filter(lab=self.lab)
		#measurement_list = sorted(chain(cont_list,disc_list), key=attrgetter('measurement_type'))
		#context['measurement_list'] = measurement_list
		measurement_list = get_measurements_from_lab(self.lab.id)
		for m in measurement_list:
			m_type = m.measurement_type
			m.warning = '⚠' if m_type.panic(m.value) else ''
			m.color = m_type.panic_color(m.value)
			m.ref = m_type.get_ref()
			m.unit = m_type.unit if m_type.unit else ''
		context['measurement_list'] = measurement_list
		has_change_perm = has_perm_for_labs(self.request.user, 'change_lab')
		has_delete_perm = has_perm_for_labs(self.request.user, 'delete_lab')
		context['change_perm'] = has_change_perm
		context['delete_perm'] = has_delete_perm
		return context


@user_passes_test(generate_has_perm_func('add_lab',raise_exception=True))
def lab_create(request, pt_id):
	pt = get_object_or_404(Patient, pk=pt_id)

	if request.method == 'POST':
		form = LabCreationForm(request.POST,pt=pt)

		if form.is_valid():
			new_lab = form.save(commit=False)
			new_lab_type = get_object_or_404(LabType,name=new_lab.lab_type)

			return redirect(reverse("labs:new-full-lab", args=(pt_id,new_lab_type.id,)))
	else:
		form = LabCreationForm(pt=pt)

	return render(request, 'labs/lab_create.html', {'form':form})


@user_passes_test(generate_has_perm_func('add_lab',raise_exception=True))
def full_lab_create(request, pt_id, lab_type_id):
	lab_type = get_object_or_404(LabType, pk=lab_type_id)
	pt = get_object_or_404(Patient, pk=pt_id)

	if request.method == 'POST':
		form = MeasurementsCreationForm(request.POST, new_lab_type=lab_type, pt=pt)

		if form.is_valid():
			lab = form.save()
			return redirect(reverse("labs:all-labs-table", args=(pt_id,)))

	else:
		form = MeasurementsCreationForm(new_lab_type=lab_type, pt=pt)
	
	return render(request, 'labs/lab_create.html', {'form':form})


@user_passes_test(generate_has_perm_func('delete_lab',raise_exception=True))
def lab_delete(request, pk):
	lab = get_object_or_404(Lab, pk=pk)
	pt = lab.patient
	lab.delete()
	return redirect(reverse("labs:all-labs", args=(pt.id,)))


@user_passes_test(generate_has_perm_func('change_lab',raise_exception=True))
def lab_edit(request, pk):
	lab = get_object_or_404(Lab, pk=pk)
	pt = lab.patient
	lab_type = lab.lab_type

	#print(request.session['clintype_pk'])
	#print(request.session)

	if request.method == 'POST':
		form = MeasurementsCreationForm(request.POST, new_lab_type=lab_type, pt=pt, lab_pk=pk)

		if form.is_valid():
			lab = form.save(lab_pk=pk)
			return redirect(reverse("labs:lab-detail", args=(pk,)))

	else:
		form = MeasurementsCreationForm(new_lab_type=lab_type, pt=pt, lab_pk=pk)
	
	return render(request, 'labs/lab_edit.html', {'form':form})



def view_all_as_table(request,pt_id,month_range=6):
	if request.method == 'GET':
		try:
			month_range = int(request.GET['select'])
		except:
			pass

	# Get qs for the patient
	pt = get_object_or_404(Patient, id=pt_id)
	lab_types = list(LabType.objects.all())
	measure_types = MeasurementType.objects.all()

	to_tz = timezone.get_default_timezone()
	time_threshold = datetime.datetime.now(to_tz) - timedelta(days=month_range*31)
	lab_qs = Lab.objects.filter(patient=pt_id, lab_time__gt=time_threshold)
	# clinic days
	lab_days = sorted(map(lambda x: x.get_day(), lab_qs), reverse=True)
	unique_lab_days=reduce(lambda l, x: l if x in l else l+[x], lab_days, [])

	listed_lab_days = unique_lab_days[:]
	n_days = len(listed_lab_days)

	# Initiate empty table
	# width = # of labs
	# height = # of measurement types


	table_header = ['','Reference']
	col_header_len = len(table_header)
	table_header += list(map(lambda x:str(x),listed_lab_days))
	table_content = []
	sorted_measure_types = []
	dup_lab_bool = False

	for t_lab_type in lab_types:
		m_types = measure_types.filter(lab_type=t_lab_type)
		#table_1col_header.append('Lab: '+str(t_lab_type))
		table_content.append([table_header[:]])
		table_content[-1][0][0] = ('Lab Category: '+str(t_lab_type))
		sorted_measure_types.append([])
		for mt in m_types:
			table_content[-1].append(([mt, mt.get_ref()] + ['']*n_days))
			sorted_measure_types[-1].append(mt)


	# Fill in entries
	for t_lab in lab_qs.reverse():
		if (not (t_lab.get_day() in listed_lab_days)):
			continue
		#cont_ms = cont_m_qs.filter(lab=t_lab)
		#dist_ms = dist_m_qs.filter(lab=t_lab)
		measurements = get_measurements_from_lab(t_lab.id)
		col_index = listed_lab_days.index(t_lab.get_day()) + col_header_len
		for m in measurements:
			section_index = lab_types.index(t_lab.lab_type)
			m_type = m.measurement_type
			row_index = (sorted_measure_types[section_index]).index(m_type)
			m.warning = '⚠' if m_type.panic(m.value) else ''
			m.color = m_type.panic_color(m.value)
			m.unit = m_type.unit if m_type.unit else ''
			#table[row_index][col_index] = str(m.value) + warning
			current_value = table_content[section_index][row_index+1][col_index]
			if current_value=='':
				table_content[section_index][row_index+1][col_index] = m
			else:
				table_content[section_index][row_index+1][col_index] = m
				table_content[section_index][0][col_index] += '*'
				dup_lab_bool = True



	qs = {'patient':pt, 
		  'labs':lab_qs, 
		  'table_content': table_content,
		  'table_header': table_header,
		  'ncol': len(table_header),
		  'add_perm':has_perm_for_labs(request.user, 'add_lab'),
		  'dup_lab_bool': dup_lab_bool}

	return render(request, 'labs/lab_all_table.html', qs)