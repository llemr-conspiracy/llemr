from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
import django.utils.timezone

from . import models as mymodels
from . import forms as myforms

import datetime


def get_current_provider():
    # this obviously needs to be different
    return get_object_or_404(mymodels.Provider, pk=1)


def get_clindates():
    clindates = mymodels.ClinicDate.objects.filter(
        clinic_date=django.utils.timezone.now().date())
    return clindates


def get_cal():
    '''Get the gcal_id of the google calendar clinic date today.
    CURRENTLY BROKEN next_date must be produced correctly.'''
    import requests

    with open('google_secret.txt') as f:
        #TODO ip-restrict access to this key for halstead only
        GOOGLE_SECRET = f.read().strip()

    calendar_id = "7eie7k06g255baksfshfhp0m28%40group.calendar.google.com"

    payload = {"key": GOOGLE_SECRET,
               "singleEvents": True,
               "timeMin": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
               "orderBy": "startTime"}

    r = requests.get("".join(["https://www.googleapis.com/calendar/v3/calendars/",
                              calendar_id,
                              '/events']),
                     params=payload)

    next_date_str = r.json()["items"][0]["start"]["dateTime"].split("T")[0].split("-")
    next_date = datetime.datetime.date(year=next_date_str[0],
                                       month=next_date_str[1],
                                       day=next_date_str[2])

    return next_date


class ClinicDateCreate(FormView):
    '''A view for creating a new ClinicDate. On submission, it redirects to
    the new-workup view.'''
    template_name = 'pttrack/clindate.html'
    form_class = myforms.ClinicDateForm

    def form_valid(self, form):
        today = datetime.datetime.date(django.utils.timezone.now())
        clindate = mymodels.ClinicDate(clinic_date=today,
                                       **form.cleaned_data)
        clindate.save()

        # determine from our URL which patient we wanted to work up before we
        # got redirected to create a clinic date
        pt = get_object_or_404(mymodels.Patient, pk=self.kwargs['pt_id'])

        return HttpResponseRedirect(reverse("new-workup", args=(pt.id,)))


class NoteFormView(FormView):
    note_type = None

    def get_context_data(self, **kwargs):
        '''Inject self.note_type as the note type.'''

        if self.note_type is None:
            raise ImproperlyConfigured("NoteCreate view must have 'note_type' variable set.")

        context = super(FormView, self).get_context_data(**kwargs)
        context['note_type'] = self.note_type

        if 'pt_id' in self.kwargs:
            context['patient'] = mymodels.Patient.objects.get(pk=self.kwargs['pt_id'])

        return context


class WorkupCreate(NoteFormView):
    '''A view for creating a new workup. Checks to see if today is a
    clinic date first, and prompts its creation if none exist.'''
    template_name = 'pttrack/form_submission.html'
    form_class = myforms.WorkupForm
    note_type = 'Workup'

    def get(self, *args, **kwargs):
        """Check that we have an instantiated ClinicDate today,
        then dispatch to get() of the superclass view."""

        clindates = get_clindates()
        pt = get_object_or_404(mymodels.Patient, pk=kwargs['pt_id'])

        if len(clindates) == 0:
            # dispatch to ClinicDateCreate because the ClinicDate doesn't exist
            return HttpResponseRedirect(reverse("new-clindate", args=(pt.id,)))
        elif len(clindates) == 1:
            # dispatch to our own view, since we know there's a ClinicDate for today
            kwargs['pt_id'] = pt.id
            print kwargs
            return super(WorkupCreate,
                         self).get(self, *args, **kwargs)
        else:  # we have >1 clindate today.
            return HttpResponseServerError(
                "<h3>We don't know how to handle >1 clinic day on a particular day!</h3>")

    def form_valid(self, form):
        pt = get_object_or_404(mymodels.Patient, pk=self.kwargs['pt_id'])
        wu = mymodels.Workup(patient=pt, **form.cleaned_data)
        wu.author = get_current_provider()
        wu.clinic_day = get_clindates()[0]

        wu.save()
        pt.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))


class FollowupCreate(NoteFormView):
    '''A view for creating a new Followup'''
    template_name = 'pttrack/form_submission.html'
    form_class = myforms.FollowupForm
    note_type = "Followup"

    def form_valid(self, form):
        pt = get_object_or_404(mymodels.Patient, pk=self.kwargs['pt_id'])
        fu = mymodels.Followup(patient=pt,
                               author=get_current_provider(),
                               **form.cleaned_data)

        fu.save()
        pt.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))


class ActionItemCreate(NoteFormView):
    '''A view for creating ActionItems using the ActionItemForm.'''
    template_name = 'pttrack/form_submission.html'
    form_class = myforms.ActionItemForm
    note_type = 'Action Item'

    def form_valid(self, form):
        '''Set the patient, provider, and written timestamp for the item.'''
        pt = get_object_or_404(mymodels.Patient, pk=self.kwargs['pt_id'])
        ai = mymodels.ActionItem(completion_date=None, author=get_current_provider(),
                                 written_date=django.utils.timezone.now(),
                                 patient=pt, **form.cleaned_data)
        ai.save()
        pt.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))


class PatientCreate(FormView):
    '''A view for creating a new patient using PatientForm.'''
    template_name = 'pttrack/intake.html'
    form_class = myforms.PatientForm

    def form_valid(self, form):
        p = mymodels.Patient(**form.cleaned_data)
        p.save()
        return HttpResponseRedirect(reverse("patient-detail", args=(p.id,)))


def done_action_item(request, ai_id):
    ai = get_object_or_404(mymodels.ActionItem, pk=ai_id)
    ai.mark_done(get_current_provider())
    ai.save()
    return HttpResponseRedirect(reverse("patient-detail", args=(ai.patient.id,)))


def reset_action_item(request, ai_id):
    ai = get_object_or_404(mymodels.ActionItem, pk=ai_id)
    ai.clear_done()
    ai.save()
    return HttpResponseRedirect(reverse("patient-detail", args=(ai.patient.id,)))
