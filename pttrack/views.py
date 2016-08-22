from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
import django.utils.timezone

from . import models as mymodels
from . import forms as myforms
from workup import models as workupmodels
import json

import datetime


def get_current_provider_type(request):
    '''
    Given the request, produce the ProviderType of the logged in user. This is
    done using session data.
    '''
    return get_object_or_404(mymodels.ProviderType,
                             pk=request.session['clintype_pk'])


def get_cal():
    '''Get the gcal_id of the google calendar clinic date today.
    CURRENTLY BROKEN next_date must be produced correctly.'''
    import requests

    with open('google_secret.txt') as f:
        # TODO ip-restrict access to this key for halstead only
        GOOGLE_SECRET = f.read().strip()

    cal_url = "https://www.googleapis.com/calendar/v3/calendars/"
    calendar_id = "7eie7k06g255baksfshfhp0m28%40group.calendar.google.com"

    payload = {"key": GOOGLE_SECRET,
               "singleEvents": True,
               "timeMin":
               datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
               "orderBy": "startTime"}

    r = requests.get("".join([cal_url,
                              calendar_id,
                              '/events']),
                     params=payload)

    # draw the first starting time out of the JSON-formatted gcal api output
    javascript_datetime = r.json()["items"][0]["start"]["dateTime"]
    next_date = javascript_datetime.split("T")[0].split("-")

    next_date = datetime.datetime.date(year=next_date_str[0],
                                       month=next_date_str[1],
                                       day=next_date_str[2])

    return next_date


class NoteFormView(FormView):
    note_type = None

    def get_context_data(self, **kwargs):
        '''Inject self.note_type and patient into the context.'''

        if self.note_type is None:
            raise ImproperlyConfigured("NoteCreate view must have" +
                                       "'note_type' variable set.")

        context = super(NoteFormView, self).get_context_data(**kwargs)
        context['note_type'] = self.note_type

        if 'pt_id' in self.kwargs:
            context['patient'] = mymodels.Patient.objects. \
                get(pk=self.kwargs['pt_id'])

        return context


class NoteUpdate(UpdateView):
    note_type = None

    def get_context_data(self, **kwargs):
        '''Inject self.note_type as the note type.'''

        if self.note_type is None:
            raise ImproperlyConfigured("NoteUpdate view must have" +
                                       "'note_type' variable set.")

        context = super(NoteUpdate, self).get_context_data(**kwargs)
        context['note_type'] = self.note_type

        return context

    # TODO: add shared form_valid code here from all subclasses.


class ProviderCreate(FormView):
    '''A view for creating a new Provider to match an existing User.'''
    template_name = 'pttrack/new-provider.html'
    form_class = myforms.ProviderForm

    def get_initial(self):
        initial = super(ProviderCreate, self).get_initial()

        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name

        return initial

    def form_valid(self, form):
        provider = form.save(commit=False)
        # check that user did not previously create a provider
        if not hasattr(self.request.user, 'provider'):
            provider.associated_user = self.request.user
            # populate the User object with the email and name data from the Provider form
            user = provider.associated_user
            user.email = form.cleaned_data['provider_email']
            user.first_name = provider.first_name
            user.last_name = provider.last_name            
            user.save()
            provider.save()
            form.save_m2m()

        return HttpResponseRedirect(self.request.GET['next'])

    def get_context_data(self, **kwargs):
        context = super(ProviderCreate, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context


class ProviderUpdate(UpdateView):
    '''
    For updating a provider, e.g. used during a new school year when preclinicals become clinicals. Set needs_update to false using require_providers_update() in pttrack.models
    '''
    template_name = 'pttrack/provider-update.html'
    model = mymodels.Provider
    form_class = myforms.ProviderForm

    def get_initial(self):
        '''
        Pre-populates email, which is a property of the User
        '''
        initial = super(ProviderUpdate, self).get_initial()
        initial['provider_email'] = self.request.user.email
        return initial

    def get_object(self):
        '''
        Returns the request's provider
        '''
        return self.request.user.provider

    def form_valid(self, form):
        provider = form.save(commit=False)
        provider.needs_updating = False
        # populate the User object with the email and name data from the Provider form
        user = provider.associated_user
        user.email = form.cleaned_data['provider_email']
        user.first_name = provider.first_name
        user.last_name = provider.last_name            
        user.save()
        provider.save()
        form.save_m2m()

        return HttpResponseRedirect(self.request.GET['next'])


class ActionItemCreate(NoteFormView):
    '''A view for creating ActionItems using the ActionItemForm.'''
    template_name = 'pttrack/form_submission.html'
    form_class = myforms.ActionItemForm
    note_type = 'Action Item'

    def form_valid(self, form):
        '''Set the patient, provider, and written timestamp for the item.'''
        pt = get_object_or_404(mymodels.Patient, pk=self.kwargs['pt_id'])
        ai = form.save(commit=False)

        ai.completion_date = None
        ai.author = self.request.user.provider
        ai.author_type = get_current_provider_type(self.request)
        ai.patient = pt

        ai.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))


class ActionItemUpdate(NoteUpdate):
    template_name = "pttrack/form-update.html"
    model = mymodels.ActionItem
    form_class = myforms.ActionItemForm
    note_type = "Action Item"

    def get_success_url(self):
        pt = self.object.patient
        return reverse("patient-detail", args=(pt.id, ))


class PatientUpdate(UpdateView):
    template_name = 'pttrack/patient-update.html'
    model = mymodels.Patient
    form_class = myforms.PatientForm

    def get_success_url(self):
        pt = self.object.patient
        return HttpResponseRedirect(reverse("patient-detail",
                                            args=(pt.id,)))


class PatientCreate(FormView):
    '''A view for creating a new patient using PatientForm.'''
    template_name = 'pttrack/intake.html'
    form_class = myforms.PatientForm

    def get_success_url(self, pt_id):
        return HttpResponseRedirect(reverse("demographics-create",
                                            args=(pt_id,)))

    def form_valid(self, form):
        pt = form.save()

        # Creating the patient indicates the patient is active (needs a workup)
        pt.needs_workup = True

        pt.save()

        return self.get_success_url(pt.id)


class DocumentUpdate(NoteUpdate):
    template_name = "pttrack/form-update.html"
    model = mymodels.Document
    form_class = myforms.DocumentForm
    note_type = "Document"

    def get_success_url(self):
        doc = self.object
        return reverse("document-detail", args=(doc.id, ))


class DocumentCreate(NoteFormView):
    '''A view for uploading a document'''
    template_name = 'pttrack/form_submission.html'
    form_class = myforms.DocumentForm
    note_type = 'Document'

    def form_valid(self, form):
        doc = form.save(commit=False)

        pt = get_object_or_404(mymodels.Patient, pk=self.kwargs['pt_id'])
        doc.patient = pt
        doc.author = self.request.user.provider
        doc.author_type = get_current_provider_type(self.request)

        doc.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))


def choose_clintype(request):
    RADIO_CHOICE_KEY = 'radio-roles'

    if request.POST:
        request.session['clintype_pk'] = request.POST[RADIO_CHOICE_KEY]
        active_provider_type = get_current_provider_type(request)
        request.session['signs_charts'] = active_provider_type.signs_charts
        request.session['staff_view'] = active_provider_type.staff_view
        return HttpResponseRedirect(request.GET['next'])

    if request.GET:
        role_options = request.user.provider.clinical_roles.all()

        if len(role_options) == 1:
            request.session['clintype_pk'] = role_options[0].pk
            active_provider_type = get_current_provider_type(request)
            request.session['signs_charts'] = active_provider_type.signs_charts
            request.session['staff_view'] = active_provider_type.staff_view
            return HttpResponseRedirect(request.GET['next'])
        elif len(role_options) == 0:
            return HttpResponseServerError(
                "Fatal: your Provider register is corrupted, and lacks " +
                "ProviderTypes. Report this error!")
        else:
            return render(request, 'pttrack/role-choice.html',
                          {'roles': role_options,
                           'choice_key': RADIO_CHOICE_KEY})


def home_page(request):

    active_provider_type = get_object_or_404(mymodels.ProviderType,
                                             pk=request.session['clintype_pk'])
    if active_provider_type.signs_charts:
        
        title = "Attending Tasks"

        lists = [{'url':'filter=unsigned_workup', 'title':"Unsigned Workups", 'identifier':'unsignedwu','active':True},
        {'url':'filter=active', 'title':"Active Patients", 'identifier':'activept', 'active':False}]

    elif active_provider_type.staff_view:
 
        title = "Coordinator Tasks"
 
        lists = [{'url':'filter=active', 'title':"Active Patients", 'identifier':'activept', 'active':True},
        {'url':'filter=ai_active', 'title':"Active Action Items", 'identifier':'activeai', 'active':False},
        {'url':'filter=ai_inactive', 'title':"Pending Action Items", 'identifier':'pendingai', 'active':False},
        {'url':'filter=unsigned_workup', 'title':"Unsigned Workups", 'identifier':'unsignedwu', 'active':False}]

    else:

        title = "Active Patients"

        lists = [{'url':'filter=ai_active', 'title':"Active Patients", 'identifier':'activept', 'active':True}]

    api_url = reverse('pt_list_api')[:-1] + '.json/?' # remove last '/' before adding because there no '/' between /api/pt_list and .json, but reverse generates '/api/pt_list/'

    return render(request,
                  'pttrack/patient_list.html',
                  {'lists': json.dumps(lists),
                    'title': title,
                    'api_url': api_url})

def patient_detail(request, pk):

    pt = get_object_or_404(mymodels.Patient, pk=pk)

    #   Special zipped list of action item types so they can be looped over. 
    #   List 1: Labels for the panel objects of the action items 
    #   List 2: Action Item lists based on type (active, pending, completed)
    #   List 3: Title labels for the action items
    #   List 4: True and False determines if the link should be for done_action_item or update_action_item

    zipped_ai_list = zip(['collapse4', 'collapse5', 'collapse6'], [pt.active_action_items(), pt.inactive_action_items(), pt.done_action_items()],
                            ['Active Action Items', 'Pending Action Items', 'Completed Action Items'], [True, True, False])

    return render(request,
                  'pttrack/patient_detail.html',
                  {'zipped_ai_list': zipped_ai_list,
                    'patient': pt})



def phone_directory(request):
    patient_list = mymodels.Patient.objects.all().order_by('last_name')

    title = "Patient Phone Number Directory"
    return render(request,
                  'pttrack/phone_directory.html',
                  {'object_list': patient_list,
                    'title': title})


def all_patients(request):

    lists = [{'url':'sort=last_name', 'title':"Alphabetized by Last Name", 'identifier':'ptlast', 'active':False},
     {'url':'sort=latest_workup', 'title':"Ordered by Latest Activity", 'identifier':'ptlatest', 'active':True}]

    api_url = reverse('pt_list_api')[:-1] + '.json/?' # remove last '/' before adding because there no '/' between /api/pt_list and .json, but reverse generates '/api/pt_list/'

    return render(request,
                  'pttrack/patient_list.html',
                  {'lists': json.dumps(lists),
                    'title': "All Patients",
                    'api_url': api_url})


def patient_activate_detail(request, pk):
    pt = get_object_or_404(mymodels.Patient, pk=pk)

    pt.toggle_active_status()

    pt.save()

    return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))

def patient_activate_home(request, pk):
    pt = get_object_or_404(mymodels.Patient, pk=pk)

    pt.toggle_active_status()

    pt.save()

    return HttpResponseRedirect(reverse("home"))

def done_action_item(request, ai_id):
    ai = get_object_or_404(mymodels.ActionItem, pk=ai_id)
    ai.mark_done(request.user.provider)
    ai.save()

    return HttpResponseRedirect(reverse("followup-choice",
                                        args=(ai.patient.pk,)))

def reset_action_item(request, ai_id):
    ai = get_object_or_404(mymodels.ActionItem, pk=ai_id)
    ai.clear_done()
    ai.save()
    return HttpResponseRedirect(reverse("patient-detail",
                                        args=(ai.patient.id,)))

