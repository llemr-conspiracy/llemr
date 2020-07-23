# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from osler.core.models import (Patient)

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from .models import *
from .forms import LabCreationForm, MeasurementsCreationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Row, HTML, Field
from crispy_forms.bootstrap import (
	InlineCheckboxes, AppendedText, PrependedText)


class LabListView(ListView):
	model = Lab
	template_name = 'labs/lab_all.html'
	context_object_name = 'labs'
	ordering = ['-written_datetime']

	def get_queryset(self):
		self.pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
		return Lab.objects.filter(patient=self.kwargs['pt_id'])


class LabDetailView(DetailView):
	model = Lab
	context_object_name = 'lab'

	def get_context_data(self, **kwargs):
		context = super(LabDetailView,self).get_context_data(**kwargs)
		self.lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
		context['cont_list'] = ContinuousMeasurement.objects.filter(lab=self.lab)
		context['disc_list'] = DiscreteMeasurement.objects.filter(lab=self.lab)
		return context


def lab_create(request, pt_id):
	pt = get_object_or_404(Patient, pk=pt_id)

	if request.method == 'POST':
		form = LabCreationForm(request.POST,pt=pt)
		if form.is_valid():
			new_lab = form.save(commit=False)
			new_lab_type = get_object_or_404(LabType,name=new_lab.lab_type)
			return redirect(reverse("new-full-lab", args=(pt_id,new_lab_type.id,)))
	else:
		form = LabCreationForm(pt=pt)

	return render(request, 'labs/lab_create.html', {'form':form})


def full_lab_create(request, pt_id, lab_type_id):
	lab_type = get_object_or_404(LabType, pk=lab_type_id)
	pt = get_object_or_404(Patient, pk=pt_id)
	qs_mt = MeasurementType.objects.filter(lab_type=lab_type)

	if request.method == 'POST':
		form = MeasurementsCreationForm(request.POST,qs_mt=qs_mt, new_lab_type=lab_type, pt=pt)

		if form.is_valid():
			lab = form.save()
			return redirect(reverse("all-labs-table", args=(pt_id,)))

	else:
		form = MeasurementsCreationForm(qs_mt=qs_mt, new_lab_type=lab_type, pt=pt)
	
	return render(request, 'labs/lab_create.html', {'form':form})


def view_all_as_table(request,pt_id,filter=''):
	# Get qs for the patient
	pt = get_object_or_404(Patient, id=pt_id)
	lab_types = LabType.objects.all()
	measure_types = MeasurementType.objects.all()

	lab_qs = Lab.objects.filter(patient=pt_id)
	cont_m_qs = ContinuousMeasurement.objects.filter(lab__in=lab_qs)
	dist_m_qs = DiscreteMeasurement.objects.filter(lab__in=lab_qs)

	# clinic days
	lab_days = map(lambda x: x.get_day(), lab_qs)
	unique_lab_days=reduce(lambda l, x: l if x in l else l+[x], lab_days, [])
	lab_months = map(lambda x: x.strftime('%Y-%m'), unique_lab_days)
	lab_months = reduce(lambda l, x: l if x in l else l+[x], lab_months, [])


	# Initiate empty table
	# width = # of labs
	# height = # of measurement types

	NEW=True

	table = []
	col_m_names = []
	sorted_measure_types = []
	num_col = len(unique_lab_days)
	header = ['Lab','Measurement']
	if NEW:
		header = ['']
	col_header_len = len(header) # 'lab', 'measurement'
	header = (header) + unique_lab_days
	print(header)


	for t_lab_type in lab_types:
		m_types = measure_types.filter(lab_type=t_lab_type)
		if NEW:
			table.append(['Lab: '+str(t_lab_type)] + ['']*num_col)
			col_m_names.append(t_lab_type)
			sorted_measure_types.append(t_lab_type)			
		for m_type in m_types:
			if NEW:
				table.append([m_type.short_name] + ['']*num_col)
			else:
				table.append([t_lab_type,m_type.short_name] + ['']*num_col)
			col_m_names.append(m_type.short_name)
			sorted_measure_types.append(m_type)


	# Fill in entries
	for i in range(len(lab_qs)):
		t_lab = lab_qs[i]
		cont_ms = cont_m_qs.filter(lab=t_lab)
		dist_ms = dist_m_qs.filter(lab=t_lab)
		col_index = unique_lab_days.index(t_lab.get_day()) + col_header_len
		for cont_m in cont_ms:
			row_index = col_m_names.index(cont_m.measurement_type.short_name)
			m_type = sorted_measure_types[row_index]
			warning = m_type.panic(cont_m.value)
			table[row_index][col_index] = str(cont_m.value) + warning
		for dist_m in dist_ms:
			row_index = col_m_names.index(dist_m.measurement_type.short_name)
			warning = '⚠⚠' if str(dist_m.value) != 'Negative' else ''
			table[row_index][col_index] = str(dist_m.value) + warning


	qs = {'patient':pt, 
		  'labs':lab_qs, 
		  'table':table,
		  'header':header,
		  'months':lab_months}

	return render(request, 'labs/lab_all_table.html', qs)
