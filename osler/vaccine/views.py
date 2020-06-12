from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import HttpResponseRedirect

from osler.core.models import Patient, ProviderType
from osler.core.views import NoteFormView
from osler.vaccine.models import VaccineSeries
from osler.vaccine.forms import (VaccineSeriesForm, VaccineDoseForm, VaccineSeriesSelectForm)

def select_vaccine_series(request,pt_id):
    """ Prompt user to select vaccine series given patient ID or create new."""
    if request.method == 'POST':
        form = VaccineSeriesSelectForm(pt_id, request.POST)
        if form.is_valid():
            # Get series from form
            series = form.cleaned_data['series']

            return HttpResponseRedirect(reverse('new-vaccine-dose',
                                            kwargs={'pt_id': pt_id,'series_id': series.id}))
    else:
        form = VaccineSeriesSelectForm(pt_id)

        return render(request,'vaccine/select-vaccine-series.html',{'form': form, 'pt_id': pt_id})


class VaccineSeriesCreate(NoteFormView):
    template_name = 'core/form_submission.html'
    note_type = "Vaccine Series"
    form_class = VaccineSeriesForm

    def form_valid(self, form):
        """Set the patient, provider, and written timestamp, and status."""
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        series = form.save(commit=False)

        # Assign author and author type
        series.author = self.request.user.provider
        series.author_type = get_object_or_404(
            ProviderType, pk=self.request.session['clintype_pk'])
        series.patient = pt

        series.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse('new-vaccine-dose',
                                            kwargs={'pt_id': pt.id,'series_id': series.id}))


class VaccineDoseCreate(NoteFormView):
    template_name = 'core/form_submission.html'
    note_type = "Vaccine Dose"
    form_class = VaccineDoseForm

    def get_form_kwargs(self):
        kwargs = super(VaccineDoseCreate, self).get_form_kwargs()

        series_id = self.kwargs['series_id']
        kwargs['series_type'] = VaccineSeries.objects.get(pk=series_id).kind

        return kwargs

    def form_valid(self, form):
        """Set the patient, provider, and written timestamp, and status."""
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        series = get_object_or_404(VaccineSeries, pk=self.kwargs['series_id'])
        dose = form.save(commit=False)

        # Assign author and author type
        dose.author = self.request.user.provider
        dose.author_type = get_object_or_404(
            ProviderType, pk=self.request.session['clintype_pk'])
        dose.patient = pt
        dose.series = series

        dose.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse('core:patient-detail', args=(pt.id,)))


# class VaccineActionItemCreate(FormView):
# 	'''Create a vaccine action item that will appear on patient homepage'''
# 	template_name = ''
#     form_class = VaccineActionItemForm


# class VaccineFollowupCreate()
