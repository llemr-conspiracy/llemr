from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from osler.core.views import NoteFormView, NoteUpdate
from osler.core.models import Patient
from osler.prescriptions import models, forms

class PrescriptionCreate(NoteFormView):
    '''A view for creating a new workup. Checks to see if today is a
    clinic date first, and prompts its creation if none exist.'''

    template_name = 'prescriptions/prescription_create.html'
    form_class = forms.PrescriptionFormSet
    model = models.Prescription
    note_type = 'Prescription'

    def get_context_data(self, **kwargs):
        context = super(PrescriptionCreate, self).get_context_data(**kwargs)
        context['prescription_form'] = context.get('form')
        return context

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])

        prescription = form.save(commit=False)
        # wu.patient = pt #will have to add a patient foreign key to prescriptions model
        prescription.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse("workup:workup-update", args=(pt.id,)))
