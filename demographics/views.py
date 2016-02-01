from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse
# Create your views here.
from . import models as mymodels
from . import forms as myforms

from pttrack.models import Patient

import datetime

class DemographicsCreate(FormView):

    template_name = 'demographics/demographics-create.html'
    form_class = myforms.DemographicsForm

    def get_context_data(self, **kwargs):

    	context = super(DemographicsCreate, self).get_context_data(**kwargs)

        if 'pt_id' in self.kwargs:
            context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])

        return context

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        
        dg = form.save(commit=False)
        dg.creation_date = datetime.date.today()
        dg.patient = pt

        if form.cleaned_data['has_insurance'] == '1':
            dg.has_insurance = True
        elif form.cleaned_data['has_insurance'] == '2':
            dg.has_insurance = False
        else:
            dg.has_insurance = None


        if form.cleaned_data['lives_alone'] == '1':
            dg.lives_alone = True
        elif form.cleaned_data['lives_alone'] == '2':
            dg.lives_alone = False
        else:
            dg.lives_alone = None

        if form.cleaned_data['currently_employed'] == '1':
            dg.currently_employed = True
        elif form.cleaned_data['currently_employed'] == '2':
            dg.currently_employed = False
        else:
            dg.currently_employed = None

        if form.cleaned_data['ER_visit_last_year'] == '1':
            dg.ER_visit_last_year = True
        elif form.cleaned_data['ER_visit_last_year'] == '2':
            dg.ER_visit_last_year = False
        else:
            dg.ER_visit_last_year = None

        dg.save()
        pt.save()
        form.save_m2m()
        form.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))

class DemographicsUpdate(UpdateView):

    template_name = 'demographics/demographics-create.html'
    form_class = myforms.DemographicsForm
    model = mymodels.Demographics


    def get_initial(self):
        initial = super(DemographicsUpdate, self).get_initial()

        dg = self.object
        
        if dg.has_insurance == True:
            initial['has_insurance'] = '1'
        elif dg.has_insurance == False:
            initial['has_insurance'] = '2'

        if dg.lives_alone == True:
            initial['lives_alone'] = '1'
        elif dg.lives_alone == False:
            initial['lives_alone'] = '2'

        if dg.currently_employed == True:
            initial['currently_employed'] = '1'
        elif dg.currently_employed == False:
            initial['currently_employed'] = '2'

        if dg.ER_visit_last_year == True:
            initial['ER_visit_last_year'] = '1'
        elif dg.ER_visit_last_year == False:
            initial['ER_visit_last_year'] = '2'

        return initial

    def form_valid(self, form):
        dg = form.save(commit=False)
        pt = dg.patient
        dg.creation_date = datetime.date.today()

        if form.cleaned_data['has_insurance'] == '1':
            dg.has_insurance = True
        elif form.cleaned_data['has_insurance'] == '2':
            dg.has_insurance = False
        else:
            dg.has_insurance = None


        if form.cleaned_data['lives_alone'] == '1':
            dg.lives_alone = True
        elif form.cleaned_data['lives_alone'] == '2':
            dg.lives_alone = False
        else:
            dg.lives_alone = None

        if form.cleaned_data['currently_employed'] == '1':
            dg.currently_employed = True
        elif form.cleaned_data['currently_employed'] == '2':
            dg.currently_employed = False
        else:
            dg.currently_employed = None

        if form.cleaned_data['ER_visit_last_year'] == '1':
            dg.ER_visit_last_year = True
        elif form.cleaned_data['ER_visit_last_year'] == '2':
            dg.ER_visit_last_year = False
        else:
            dg.ER_visit_last_year = None

        dg.save()
        form.save_m2m()
        form.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))


