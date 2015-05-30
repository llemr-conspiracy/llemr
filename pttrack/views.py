from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the BIG TABLE.")


def clindate(request, clindate):
    (year, month, day) = clindate.split("-")

    return HttpResponse("Clinic date %s" % year+" "+month+" "+day)


def patient(request, pt_uuid):
    return HttpResponse("You're looking at patient %s" % pt_uuid)


def intake(request):
    from . import forms as myforms

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = myforms.PatientForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = myforms.PatientForm()

    return render(request, 'pttrack/intake.html', {'form': form})

def newpatient(request):
    return HttpResponse("You added a patient")