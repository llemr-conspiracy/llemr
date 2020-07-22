from __future__ import unicode_literals
import collections

from django.urls import reverse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.utils.timezone import now

from osler.core.views import (NoteFormView, NoteUpdate,
                                 get_current_provider_type)
from osler.core.models import Patient

from osler.appointment.models import Appointment
from osler.appointment.forms import AppointmentForm


def list_view(request):

    # Want to sort the list so earliest dates are first
    appointments = Appointment.objects.filter(
        clindate__gte=now().date()).order_by('clindate', 'clintime')
    d = collections.OrderedDict()
    for a in appointments:
        if a.clindate in d:
            d[a.clindate].append(a)
        else:
            d[a.clindate] = [a]

    return render(request, 'appointment/appointment_list.html',
                  {'appointments_by_date': d})


def mark_no_show(request, pk):
    """Mark a patient as having not shown to an appointment
    """

    apt = get_object_or_404(Appointment, pk=pk)
    apt.pt_showed = False
    apt.save()

    return HttpResponseRedirect(reverse("appointment-list"))


def mark_arrived(request, pk):
    """Mark a patient as having arrived to an appointment
    """

    apt = get_object_or_404(Appointment, pk=pk)
    apt.pt_showed = True
    apt.save()

    return HttpResponseRedirect(reverse("core:patient-update", args=(apt.patient.pk,)))



class AppointmentUpdate(NoteUpdate):
    template_name = "core/form-update.html"
    model = Appointment
    form_class = AppointmentForm
    note_type = "Appointment"
    success_url = "/appointment/list"


class AppointmentCreate(NoteFormView):
    template_name = 'appointment/form_submission.html'
    note_type = "Appointment"
    form_class = AppointmentForm
    success_url = "list"

    def form_valid(self, form):
        appointment = form.save(commit=False)
        appointment.author = self.request.user.provider
        appointment.author_type = get_current_provider_type(self.request)

        appointment.save()

        return HttpResponseRedirect(reverse("appointment-list"))

    def get_initial(self):
        initial = super(AppointmentCreate, self).get_initial()
        pt_id = self.request.GET.get('pt_id', None)
        if pt_id is not None:
            patient = get_object_or_404(Patient, pk=pt_id)
            initial['patient'] = patient

        date = self.request.GET.get('date', None)
        if date is not None:
            # If appointment attribute clindate = workup.models.ClinicDate,
            # default date could be next clindate.
            # For now, the default value will be the next Saturday (including day of)
            initial['clindate'] = date

        return initial
