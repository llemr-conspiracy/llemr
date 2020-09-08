from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import HttpResponseRedirect

from osler.core.models import Patient
from osler.core.views import NoteFormView
from osler.core.utils import get_due_date_from_url_query_dict
from osler.users.utils import get_active_role
from osler.followup.views import FollowupCreate
from osler.vaccine.models import VaccineSeries, VaccineActionItem
from osler.vaccine.forms import (VaccineSeriesForm, VaccineDoseForm,
    VaccineSeriesSelectForm, VaccineFollowup, VaccineActionItemForm)

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
    '''Create a vaccine series for a patient'''
    template_name = 'core/form_submission.html'
    note_type = "Vaccine Series"
    form_class = VaccineSeriesForm

    def form_valid(self, form):
        """Set the patient, author, and written timestamp, and status."""
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        series = form.save(commit=False)

        # Assign author and author type
        series.author = self.request.user
        series.author_type = get_active_role(self.request)
        series.patient = pt

        series.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse('new-vaccine-dose',
                                            kwargs={'pt_id': pt.id,'series_id': series.id}))


class VaccineDoseCreate(NoteFormView):
    '''Create individual doses for a given vaccine series for a patient'''
    template_name = 'core/form_submission.html'
    note_type = "Vaccine Dose"
    form_class = VaccineDoseForm

    def get_form_kwargs(self):
        kwargs = super(VaccineDoseCreate, self).get_form_kwargs()

        series_id = self.kwargs['series_id']
        kwargs['series_type'] = VaccineSeries.objects.get(pk=series_id).kind

        return kwargs

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        series = get_object_or_404(VaccineSeries, pk=self.kwargs['series_id'])
        dose = form.save(commit=False)

        # Assign author and author type
        dose.author = self.request.user
        dose.author_type = get_active_role(self.request)
        dose.patient = pt
        dose.series = series

        dose.save()
        form.save_m2m()

        if dose.is_last():
            return HttpResponseRedirect(reverse('core:patient-detail', args=(pt.id,)))
        else:
            formatted_date = dose.next_due_date().strftime("%D")
            querystr = '%s=%s' % ("due_date", formatted_date)
            vai_url = "%s?%s" % (reverse('new-vaccine-ai',
                kwargs={'pt_id': pt.id, 'series_id': series.id}), querystr)
            return HttpResponseRedirect(vai_url)


class VaccineActionItemCreate(NoteFormView):
    '''Create a vaccine action item that will appear on patient homepage'''
    template_name = 'core/form_submission.html'
    form_class = VaccineActionItemForm
    note_type = 'Vaccine Action Item'

    def get_initial(self):
        initial = super(VaccineActionItemCreate, self).get_initial()

        initial.update(get_due_date_from_url_query_dict(self.request))
        return initial

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        vai = form.save(commit=False)

        vai.completion_date = None
        vai.author = self.request.user
        vai.author_type = get_active_role(self.request)
        vai.vaccine = get_object_or_404(
            VaccineSeries, pk=self.kwargs['series_id'])
        vai.patient = pt
        vai.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse('core:patient-detail', args=(pt.id,)))


class VaccineFollowupCreate(FollowupCreate):
    '''A view for creating a new VaccineFollowup'''
    form_class = VaccineFollowup

    def get_form_class(self,**kwargs):
        return self.form_class

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        vai = get_object_or_404(VaccineActionItem, pk=self.kwargs['ai_id'])

        vai.mark_done(self.request.user)
        vai.save()

        vai_fu = form.save(commit=False)
        vai_fu.author = self.request.user
        vai_fu.author_type = get_active_role(self.request)
        vai_fu.action_item = vai
        vai_fu.patient = pt
        vai_fu.save()
        form.save_m2m()

        if 'followup_create' in self.request.POST:
            return HttpResponseRedirect(reverse('new-vaccine-ai',
                kwargs={'pt_id': pt.id, 'series_id': vai.vaccine.id}))
        else:
            return HttpResponseRedirect(reverse("core:patient-detail",
                                                args=(pt.id,)))
