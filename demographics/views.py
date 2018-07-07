import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.forms.models import model_to_dict

from django.shortcuts import render

# Create your views here.
from .models import Demographics
from .forms import DemographicsForm

from pttrack.models import Patient


class DemographicsCreate(FormView):

    template_name = 'demographics/demographics-create.html'
    form_class = DemographicsForm

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
            with transaction.atomic():
                dg.save()
                pt.save()
                form.save_m2m()
                form.save()
            return HttpResponseRedirect(reverse("patient-detail",
                                                args=(pt.id,)))
        except IntegrityError:
            # Create form object containing data from current entry in database
            dg_old = Demographics.objects.get(patient=pt.id)
            form_old = DemographicsForm(dg_old.__dict__)

            # calling is_valid causes cleaned_data to be availiable
            assert form_old.is_valid()

            NULL_BOOLEAN_CHOICES = dict(Demographics.NULL_BOOLEAN_CHOICES)

            # Add errors to the forms to point user to fields to fix
            dg_old_dict = model_to_dict(dg_old)
            dg_new_dict = model_to_dict(dg)

            for field in form_old.base_fields:

                old_value = dg_old_dict.get(field)
                new_value = dg_new_dict.get(field)

                if new_value != old_value:

                    new_err_msg = "Clash in this field. You entered '%s'"
                    old_err_msg = "Clash in this field. Database entry is '%s'"

                    value_msg_form_tuples = [
                        (new_value, new_err_msg, form),
                        (old_value, old_err_msg, form_old)
                    ]

                    for val, err_msg, f in value_msg_form_tuples:
                        if val in NULL_BOOLEAN_CHOICES:
                            err_msg = err_msg % NULL_BOOLEAN_CHOICES[val]
                        else:
                            err_msg = err_msg % val

                        f.add_error(field, err_msg)

            # Create context variable containing new and old forms
            context = {"form_old": form_old,
                       "form_new": form,
                       "pt_id": pt.id,
                       "pt_name": pt.name}
            return render(self.request,
                          "demographics/demographics-resolve.html",
                          context)


class DemographicsUpdate(UpdateView):

    template_name = 'demographics/demographics-create.html'
    form_class = DemographicsForm
    model = Demographics

    def get_initial(self):
        initial = super(DemographicsUpdate, self).get_initial()

        return initial

    def form_valid(self, form):
        dg = form.save(commit=False)
        pt = dg.patient
        dg.creation_date = datetime.date.today()

        dg.save()
        form.save_m2m()
        form.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))
