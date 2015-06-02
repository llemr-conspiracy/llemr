from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import django.utils.timezone

from . import models as mymodels
from . import forms as myforms

import datetime


def get_current_provider():
    return mymodels.Provider.objects.get(id=1)


def get_cal():
    import requests

    calendar_id = "7eie7k06g255baksfshfhp0m28%40group.calendar.google.com"

    payload = {"key": GOOGLE_SECRET,
               "singleEvents": True,
               # "timeMin": datetime.datetime.now(),
               "orderBy": "startTime"}

    r = requests.get("".join(["https://www.googleapis.com/calendar/v3/calendars/",
                              calendar_id,
                              '/events']),
                     params=payload)

    return r.json()


def index(request):
    model = mymodels.Patient


def clindate(request, clindate):
    (year, month, day) = clindate.split("-")

    return HttpResponse("Clinic date %s" % year+" "+month+" "+day)


def workup(request, pt_id):

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
        clindates = mymodels.ClinicDate.objects.filter(
            clinic_date=django.utils.timezone.now)

        if len(clindates) == 1:
            return render(request, 'pttrack/workup.html', {"patient": pt,
                                                           "form": myforms.WorkupForm()})
        elif len(clindates) == 0:
            return render(request, 'pttrack/clindate.html', {"patient": pt,
                                                             "form": myforms.ClinicDateForm()})

        else:
            pass


def followup(request, pt_id):

    if request.method == 'POST':
        pt = get_object_or_404(mymodels.Patient, pk=pt_id)
        form = myforms.FollowupForm(request.POST)

        if form.is_valid():
            fu = mymodels.Followup(patient=pt, **form.cleaned_data)
            fu.written_date = django.utils.timezone.now

            #TODO: use authentication to determine provider
            fu.author = get_current_provider()
            fu.save()
            pt.save()

            return HttpResponseRedirect(reverse("patient", args=(pt.id,)))

    else:
        pt = get_object_or_404(mymodels.Patient, pk=pt_id)
        form = myforms.FollowupForm()
        # action_item = myforms.ActionItemForm()

        return render(request, 'pttrack/followup.html', {'patient': pt,
                                                         'form': form})


def patient(request, pt_id):
    pt = get_object_or_404(mymodels.Patient, pk=pt_id)

    return render(request, 'pttrack/patient.html', {'patient': pt})


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

    # if a GET (or any other method) we'll create a blank form
    else:
        form = myforms.PatientForm()

    return render(request, 'pttrack/intake.html', {'form': form})
