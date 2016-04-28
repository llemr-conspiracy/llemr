from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
import django.utils.timezone

from . import models as mymodels
from . import forms as myforms

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

    def form_valid(self, form):
        pt = form.save()

        if not '-' in pt.ssn:
            pt.ssn = pt.ssn[0:3] + '-' + pt.ssn[3:5] + '-' + pt.ssn[5:]

        pt.save()
        return HttpResponseRedirect(reverse("patient-detail",  
                                            args=(pt.id,)))


class PatientCreate(FormView):
    '''A view for creating a new patient using PatientForm.'''
    template_name = 'pttrack/intake.html'
    form_class = myforms.PatientForm

    def form_valid(self, form):
        pt = form.save()

        # Action of creating the patient should indicate the patient is active (needs a workup)
        pt.needs_workup = True

        if not '-' in pt.ssn:
            pt.ssn = pt.ssn[0:3] + '-' + pt.ssn[3:5] + '-' + pt.ssn[5:]

        pt.save()
        return HttpResponseRedirect(reverse("demographics-create",  
                                            args=(pt.id,)))


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

    #TODO wow so this is messed up. This should be a circular dependency...
    from workup.models import Workup

    active_provider_type = get_object_or_404(mymodels.ProviderType,
                                             pk=request.session['clintype_pk'])
    if active_provider_type.signs_charts:
        
        wu_list_unsigned = Workup.objects.filter(signer__isnull=True).select_related('patient')
        pt_list_unsigned = list(set([wu.patient for wu in wu_list_unsigned]))
        pt_list_unsigned.sort(key = lambda pt: pt.last_name)

        pt_list_active = mymodels.Patient.objects.filter(needs_workup__exact=True).order_by('last_name')
        
        title = "Attending Tasks"
        zipped_list = zip(["Patients with Unsigned Workups", "Active Patients"],
                            [pt_list_unsigned, pt_list_active],
                            ["unsignedwu", "activept"],
                            [True, False])

    elif active_provider_type.staff_view:
        
        pt_list_active = mymodels.Patient.objects.filter(needs_workup__exact=True).order_by('last_name')
        ai_list_active = mymodels.ActionItem.objects.filter(due_date__lte=django.utils.timezone.now().date())
        pt_list_ai_active = list(set([ai.patient for ai in ai_list_active if not ai.done()]))

        ai_list_inactive = mymodels.ActionItem.objects.filter(due_date__gt=django.utils.timezone.now().date()).order_by('due_date')
        pt_list_ai_inactive = list(set([ai.patient for ai in ai_list_inactive if not ai.done()]))
        pt_list_ai_inactive.sort(key = lambda pt: pt.inactive_action_items()[-1].due_date)

        wu_list_unsigned = Workup.objects.filter(signer__isnull=True).select_related('patient')
        pt_list_unsigned = list(set([wu.patient for wu in wu_list_unsigned]))
        pt_list_unsigned.sort(key = lambda pt: pt.last_name)

        title = "Coordinator Tasks"
        zipped_list = zip(["Active Patients", "Active Action Items", "Pending Action Items", "Unsigned Workups"], 
                            [pt_list_active, pt_list_ai_active, pt_list_ai_inactive, pt_list_unsigned],
                            ["activept", "activeai", "pendingai", "unsignedwu"],
                            [True, False, False, False])

    else:
        pt_list_active = mymodels.Patient.objects.filter(needs_workup__exact=True).order_by('last_name')

        title = "Active Patients"
        zipped_list = zip(["Active Patients"],
                        [pt_list_active],
                        ["activept"],
                        [True])

    return render(request,
                  'pttrack/patient_list.html',
                  {'zipped_list': zipped_list,
                    'title': title})

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
    pt_list_last = list(mymodels.Patient.objects.all().order_by('last_name'))
    pt_list_first = list(mymodels.Patient.objects.all().order_by('first_name'))
    pt_list_latest = list(mymodels.Patient.objects.all())

    def bylatestKey(pt):
        latestwu = pt.latest_workup()
        if latestwu == None:
            latestdate = pt.history.last().history_date.date()
        else:
            latestdate = latestwu.clinic_day.clinic_date
        return latestdate

    pt_list_latest.sort(key = bylatestKey, reverse=True)

    zipped_list = zip(["Alphabetized by Last Name", "Alphabetized by First Name", "Ordered by Latest Activity"],
                        [pt_list_last, pt_list_first, pt_list_latest],
                        ['ptlast', 'ptfirst', 'ptlatest'],
                        [False, False, True])
    return render(request,
                  'pttrack/patient_list.html',
                  {'zipped_list': zipped_list,
                    'title': "All Patients"})


def patient_activate_detail(request, pk):
    pt = get_object_or_404(mymodels.Patient, pk=pk)

    pt.change_active_status()

    pt.save()

    return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))

def patient_activate_home(request, pk):
    pt = get_object_or_404(mymodels.Patient, pk=pk)

    pt.change_active_status()

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
