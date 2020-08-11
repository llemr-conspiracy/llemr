from functools import reduce
from osler.core.models import (Patient)
from django.contrib.auth.decorators import permission_required

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
		context['add_perm'] = self.request.user.has_perm('labs.add_lab')
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
		context['measurement_list'] = measurement_list
		context['change_perm'] = self.request.user.has_perm('labs.change_lab')
		context['delete_perm'] = self.request.user.has_perm('labs.delete_lab')
		return context


@permission_required('labs.add_lab', raise_exception=True)
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


@permission_required('labs.add_lab', raise_exception=True)
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


@permission_required('labs.delete_lab', raise_exception=True)
def lab_delete(request, pk):
	lab = get_object_or_404(Lab, pk=pk)
	pt = lab.patient
	lab.delete()
	return redirect(reverse("labs:all-labs", args=(pt.id,)))


@permission_required('labs.change_lab', raise_exception=True)
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
	
	return render(request, 'labs/lab_create.html', {'form':form})


def view_all_as_table_old(request,pt_id,filter=''):
	# Get qs for the patient
	pt = get_object_or_404(Patient, id=pt_id)
	lab_types = LabType.objects.all()
	measure_types = MeasurementType.objects.all()

	lab_qs = Lab.objects.filter(patient=pt_id)
	cont_m_qs = ContinuousMeasurement.objects.filter(lab__in=lab_qs)
	dist_m_qs = DiscreteMeasurement.objects.filter(lab__in=lab_qs)

	# clinic days
	lab_days = sorted(map(lambda x: x.get_day(), lab_qs), reverse=True)
	unique_lab_days=reduce(lambda l, x: l if x in l else l+[x], lab_days, [])
	lab_months = map(lambda x: x.strftime('%Y-%m'), unique_lab_days)
	lab_months = reduce(lambda l, x: l if x in l else l+[x], lab_months, [])


	# Initiate empty table
	# width = # of labs
	# height = # of measurement types

	NEW=True

	table = []
	table_col_header = []
	sorted_measure_types = []
	num_col = len(unique_lab_days)
	header = ['Lab','Measurement']
	if NEW:
		header = ['','Reference']
	col_header_len = len(header) # 'lab', 'measurement'
	header = (header) + unique_lab_days


	for t_lab_type in lab_types:
		m_types = measure_types.filter(lab_type=t_lab_type)
		if NEW:
			table.append(['Lab: '+str(t_lab_type)] + ['']*(num_col+1))
			table_col_header.append(t_lab_type)
			sorted_measure_types.append(t_lab_type)			
		for m_type in m_types:
			if NEW:
				ref = m_type.get_ref()
				table.append([m_type.short_name, ref] + ['']*num_col)
			else:
				table.append([t_lab_type,m_type.short_name] + ['']*num_col)
			table_col_header.append(m_type.short_name)
			sorted_measure_types.append(m_type)


	# Fill in entries
	for i in range(len(lab_qs)):
		t_lab = lab_qs[i]
		cont_ms = cont_m_qs.filter(lab=t_lab)
		dist_ms = dist_m_qs.filter(lab=t_lab)
		col_index = unique_lab_days.index(t_lab.get_day()) + col_header_len
		for cont_m in cont_ms:
			row_index = table_col_header.index(cont_m.measurement_type.short_name)
			m_type = sorted_measure_types[row_index]
			warning = '⚠' if m_type.panic(cont_m.value) else ''
			table[row_index][col_index] = str(cont_m.value) + warning
		for dist_m in dist_ms:
			row_index = table_col_header.index(dist_m.measurement_type.short_name)
			m_type = sorted_measure_types[row_index]
			warning = '⚠' if m_type.panic(dist_m.value) else ''
			table[row_index][col_index] = str(dist_m.value) + warning


	qs = {'patient':pt, 
		  'labs':lab_qs, 
		  'table':table,
		  'header':header,
		  'months':lab_months+['All'],
		  'add_perm':request.user.has_perm('labs.add_lab')}

	return render(request, 'labs/lab_all_table.html', qs)




def view_all_as_table(request,pt_id,filter=''):
	# Get qs for the patient
	pt = get_object_or_404(Patient, id=pt_id)
	lab_types = list(LabType.objects.all())
	measure_types = MeasurementType.objects.all()

	lab_qs = Lab.objects.filter(patient=pt_id)
	# clinic days
	lab_days = sorted(map(lambda x: x.get_day(), lab_qs), reverse=True)
	unique_lab_days=reduce(lambda l, x: l if x in l else l+[x], lab_days, [])
	lab_months = map(lambda x: x.strftime('%Y-%m'), unique_lab_days)
	lab_months = reduce(lambda l, x: l if x in l else l+[x], lab_months, [])

	listed_lab_days = unique_lab_days[:1]
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
		  'months':lab_months+['All'],
		  'table_content': table_content,
		  'table_header': table_header,
		  'ncol': len(table_header),
		  'add_perm':request.user.has_perm('labs.add_lab'),
		  'dup_lab_bool': dup_lab_bool}

	return render(request, 'labs/lab_all_table.html', qs)