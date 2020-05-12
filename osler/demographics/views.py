from __future__ import unicode_literals
import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.forms.models import model_to_dict
from django.shortcuts import render

from osler.core.models import Patient
from osler.demographics.models import Demographics
from osler.demographics.forms import DemographicsForm


class DemographicsCreate(FormView):

    template_name = 'demographics/demographics-create.html'
    form_class = DemographicsForm

    def get_context_data(self, **kwargs):

        context = super(DemographicsCreate, self).get_context_data(**kwargs)

        if 'pt_id' in self.kwargs:
            context['patient'] = Patient.objects.get(pk=self.kwargs['pt_id'])

        return context

    def form_valid(self, form_new):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])

        dg_new = form_new.save(commit=False)
        dg_new.creation_date = datetime.date.today()
        dg_new.patient = pt

        try:
            with transaction.atomic():
                dg_new.save()
                pt.save()
                form_new.save_m2m()
                form_new.save()
            return HttpResponseRedirect(reverse("core:patient-detail",
                                                args=(pt.id,)))
        except IntegrityError:

            # Create form object containing data from current entry in database
            dg_old = Demographics.objects.get(patient=pt.id)

            dgdict_new = model_to_dict(dg_new)
            dgdict_old = model_to_dict(dg_old)

            differences = [k for k, v in dgdict_old.items() if
                           k not in ['_state', 'id'] and
                           dgdict_new[k] != v]

            # An integrity error will be thrown whether or not there is
            # a difference between the models.
            if not differences:
                return HttpResponseRedirect(reverse("core:patient-detail",
                                            args=(pt.id,)))

            form_old = DemographicsForm(dg_old.__dict__)
            assert form_old.is_valid()

            for field in differences:

                new_val = form_new[field].value()
                old_val = form_old[field].value()

                if new_val != old_val:

                    form_old.add_error(
                        field,
                        "Clash in this field. Database entry is '%s'" %
                        old_val
                        # (old_val if old_val is not None else 'Not Answered')
                    )

                    form_new.add_error(
                        field,
                        "Clash in this field. You entered '%s'" %
                        new_val
                        # (new_val if new_val is not None else 'Not Answered')
                    )

            # Create context variable containing new and old forms
            context = {"form_old": form_old,
                       "form_new": form_new,
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

        return HttpResponseRedirect(reverse("core:patient-detail", args=(pt.id,)))
