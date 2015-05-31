from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from . import models as mymodels
from . import forms as myforms

import datetime

# Create your views here.from django.http import HttpResponse


def index(request):
    model= mymodels.Patient

def clindate(request, clindate):
    (year, month, day) = clindate.split("-")

    return HttpResponse("Clinic date %s" % year+" "+month+" "+day)


def followup(request, pt_id):
    pt = get_object_or_404(mymodels.Patient, pk=pt_id)
    form = myforms.FollowupForm(request.POST)

    if form.is_valid():
        fu = mymodels.Followup(**form.cleaned_data)
        fu.written_date = datetime.datetime.now()
        fu.patient = pt
        fu.save()
        pt.save()

        return HttpResponseRedirect(reverse("patient", args=(pt.id,)))


def patient(request, pt_id):
    pt = get_object_or_404(mymodels.Patient, pk=pt_id)

    workup_form = myforms.WorkupForm()
    followup_form = myforms.FollowupForm()

    return render(request, 'pttrack/patient.html', {'patient': pt,
                                                    'workup_form': workup_form,
                                                    'followup_form': followup_form
                                                    })


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
