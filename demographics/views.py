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
        dg.save()
        pt.demographics = dg
        pt.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))

class DemographicsUpdate(UpdateView):

    template_name = 'demographics/demographics-create.html'
    form_class = myforms.DemographicsForm
    model = mymodels.Demographics

    def get_success_url(self):
        return reverse('demographics-detail', args=(self.object.id,))


