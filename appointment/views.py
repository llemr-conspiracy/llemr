from django.core.urlresolvers import reverse
from django.shortcuts import render, HttpResponseRedirect

from pttrack.views import NoteFormView, NoteUpdate, get_current_provider_type

from .models import Appointment
from .forms import AppointmentForm
import datetime


def list_view(request):

    # Want to sort the list so earliest dates are first
    appointments = Appointment.objects.filter(clindate__gte=datetime.date.today())
    print(appointments)
    d = {}
    for a in appointments:
        if a.clindate in d:
            d[a.clindate].append(a)
        else:
            d[a.clindate] = [a]
    print(d)
    return render(request, 'appointment/appointment_list.html',
                  {'appointments_by_date': d})

class AppointmentUpdate(NoteUpdate):
    template_name = "pttrack/form-update.html"
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

