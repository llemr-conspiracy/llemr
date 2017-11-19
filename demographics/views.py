from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.shortcuts import render

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

        try:
            dg.save()
            pt.save()
            form.save_m2m()
            form.save()
            return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))
        except IntegrityError:
            # Create form object containing data from current entry in database
            dg_old = mymodels.Demographics.objects.get(pk=pt.id)
            form_old = myforms.DemographicsForm(dg_old.__dict__)

            # Add errors to the forms to point user to fields to fix

            # Create dictionary mapping database entries to front-end choices 
            # for use in error messages
            NULL_BOOLEAN_CHOICES = dict([
                (None, "Not Answered"),
                (True, "Yes"),
                (False, "No")
            ])

            if form_old.is_valid():
                for field, old_value in form_old.cleaned_data.items():
                    new_value = form.cleaned_data.get(field)
                    if new_value != old_value:

                        new_error_message = "Clash in this field. You entered '"
                        old_error_message = "Clash in this field. Database entry was '"

                        if NULL_BOOLEAN_CHOICES.get(new_value) != None:
                            new_error_message = new_error_message + "%s'" % NULL_BOOLEAN_CHOICES[new_value]
                        else:
                            new_error_message = new_error_message + "%s'" % new_value

                        if NULL_BOOLEAN_CHOICES.get(old_value) != None:
                            old_error_message = old_error_message + "%s'" % NULL_BOOLEAN_CHOICES[old_value]
                        else:
                            old_error_message = old_error_message + "%s'" % old_value

                        form_old.add_error(field, old_error_message)
                        form.add_error(field, new_error_message)


            # Create context variable containing new and old forms
            context = {"form_old": form_old,
                       "form_new": form,
                       "pt_id": pt.id,
                       "pt_name": pt.name}
            return render(self.request, "demographics/demographics-resolve.html", context)


class DemographicsUpdate(UpdateView):

    template_name = 'demographics/demographics-create.html'
    form_class = myforms.DemographicsForm
    model = mymodels.Demographics

    def get_initial(self):
        initial = super(DemographicsUpdate, self).get_initial()

        dg = self.object

        return initial

    def form_valid(self, form):
        dg = form.save(commit=False)
        pt = dg.patient
        dg.creation_date = datetime.date.today()

        dg.save()
        form.save_m2m()
        form.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))



