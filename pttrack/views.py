from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.core.urlresolvers import reverse
import django.utils.timezone

from . import models as mymodels
from . import forms as myforms

import datetime


def get_current_provider():
    return get_object_or_404(mymodels.Provider, pk=1)


def get_cal():
    '''Get the gcal_id of the google calendar clinic date today.
    CURRENTLY BROKEN next_date must be produced correctly.'''
    import requests

    with open('google_secret.txt') as f:
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


def clindate(request, pt_id):
    if request.method == 'POST':

        form = myforms.ClinicDateForm(request.POST)

        if form.is_valid():
            today = datetime.datetime.date(django.utils.timezone.now())
            clindate = mymodels.ClinicDate(clinic_date=today,
                                           **form.cleaned_data)
            clindate.save()
        else:
            pass  # error reporting goes here

    return redirect(reverse('new-workup', args=(pt_id,)))


def new_workup(request, pt_id):

    pt = get_object_or_404(mymodels.Patient, pk=pt_id)
    clindates = mymodels.ClinicDate.objects.filter(
        clinic_date=django.utils.timezone.now)

    if request.method == 'POST':
        clindate = clindates[0]
        form = myforms.WorkupForm(request.POST)

        if form.is_valid():
            wu = mymodels.Workup(patient=pt, **form.cleaned_data)
            wu.author = get_current_provider()
            wu.clinic_day = clindate

            wu.save()
            pt.save()

            return HttpResponseRedirect(reverse("patient", args=(pt.id,)))
        else:
            pass  # error reporting goes here

    else:
        clindates = mymodels.ClinicDate.objects.filter(
            clinic_date=django.utils.timezone.now)

        if len(clindates) == 1:
            return render(request, 'pttrack/form_submission.html',
                          {"patient": pt, "form": myforms.WorkupForm(), "note_type": "Workup"})
        elif len(clindates) == 0:
            return render(request, 'pttrack/clindate.html', {"patient": pt,
                                                             "form": myforms.ClinicDateForm()})
        else:
            HttpResponseServerError(
                "<h3>We don't know how to handle >1 clinic day on a particular day!</h3>")


def followup(request, pt_id):

    if request.method == 'POST':
        pt = get_object_or_404(mymodels.Patient, pk=pt_id)
        form = myforms.FollowupForm(request.POST)

        if form.is_valid():
            fu = mymodels.Followup(patient=pt, **form.cleaned_data)
            fu.written_date = django.utils.timezone.now()

            #TODO: use authentication to determine provider
            fu.author = get_current_provider()
            fu.save()
            pt.save()

            return HttpResponseRedirect(reverse("patient", args=(pt.id,)))
        else:
            pass  # error reporting goes here

    else:
        pt = get_object_or_404(mymodels.Patient, pk=pt_id)
        form = myforms.FollowupForm()
        # action_item = myforms.ActionItemForm()

        return render(request, 'pttrack/form_submission.html',
                      {'patient': pt, 'form': form, 'note_type': 'Followup'})


def new_action_item(request, pt_id):
    pt = get_object_or_404(mymodels.Patient, pk=pt_id)
    form = myforms.ActionItemForm()

    return render(request, 'pttrack/form_submission.html',
                  {'patient': pt, 'form': form, 'note_type': 'Action Item'})


def patient(request, pt_id):
    pt = get_object_or_404(mymodels.Patient, pk=pt_id)

    notes = list(pt.workup_set.all())
    notes.extend(pt.followup_set.all())

    return render(request, 'pttrack/patient.html', {'patient': pt,
                                                    'notes': notes})


def intake(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = myforms.PatientForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            p = mymodels.Patient(**form.cleaned_data)
            p.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse("patient", args=(p.id,)))
        else:
            pass  #error reporting goes here


    # if a GET (or any other method) we'll create a blank form
    else:
        form = myforms.PatientForm()

    return render(request, 'pttrack/intake.html', {'form': form})
