import json
import collections
import datetime

from django.conf import settings
from django.apps import apps
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Prefetch
from django.utils.http import is_safe_url

from django_registration.backends.one_step import views

from workup import models as workupmodels
from referral.models import Referral, FollowupRequest, PatientContact
from appointment.models import Appointment

from . import models as mymodels
from . import forms as myforms
from . import utils


def get_current_provider_type(request):
    '''
    Given the request, produce the ProviderType of the logged in user. This is
    done using session data.
    '''
    return get_object_or_404(mymodels.ProviderType,
                             pk=request.session['clintype_pk'])


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
            user.is_staff = True  # for a demo, all users are staff
            user.is_superuser = True  # for a demo, all users are staff
            user.save()
            provider.save()
            form.save_m2m()

        return HttpResponseRedirect(self.request.GET['next'])

    def get_context_data(self, **kwargs):
        context = super(ProviderCreate, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context


class ProviderUpdate(UpdateView):
    """For updating a provider, e.g. used during a new school year when
    preclinicals become clinicals. Set needs_update to false using
    require_providers_update() in pttrack.models
    """
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

    def form_valid(self, form):
        pt = form.save()
        pt.save()

        return HttpResponseRedirect(reverse("patient-detail",
                                            args=(pt.id,)))


class PreIntakeSelect(ListView):
    """Allows users to see all patients with similar name to a
    particular patient first and last name. Allows user to open one of
    the simmilarly named patients, or create a new patient
    """
    template_name = 'pttrack/preintake-select.html'
    new_pt_url = ""

    def parse_url_querystring(self):

        return utils.get_names_from_url_query_dict(self.request)

    def get_queryset(self):
        initial = self.parse_url_querystring()
        if (initial.get('first_name', None) is None or
            initial.get('last_name', None) is None):
            return []
        possible_duplicates = utils.return_duplicates(initial.get(
            'first_name', None), initial.get('last_name', None))
        return possible_duplicates

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PreIntakeSelect, self).get_context_data(**kwargs)
        initial = self.parse_url_querystring()
        context['first_name'] = initial.get('first_name', None)
        context['last_name'] = initial.get('last_name', None)
        context['new_pt_url'] = "%s?%s=%s&%s=%s" % (
            reverse("intake"),
            "first_name", initial.get('first_name', None),
            "last_name", initial.get('last_name', None))
        context['home'] = reverse("home")
        return context


class PreIntake(FormView):
    """A view for ensuring new patient is not already in the database.

    Searches if there is a patient with same, or similar first and last
    name. If none similar directs to patient intake;  If one or more similar
    directs to preintake-select urls are sent with first and last name in
    query string notation
    """

    template_name = 'pttrack/preintake.html'
    form_class = myforms.DuplicatePatientForm

    def form_valid(self, form):
        first_name_str = form.cleaned_data['first_name'].capitalize()
        last_name_str = form.cleaned_data['last_name'].capitalize()
        matching_patients = utils.return_duplicates(first_name_str,
                                                    last_name_str)

        querystr = '%s=%s&%s=%s' % ("first_name", first_name_str,
                                    "last_name", last_name_str)
        if len(matching_patients) > 0:
            intake_url = "%s?%s" % (reverse("preintake-select"), querystr)
            return HttpResponseRedirect(intake_url)

        intake_url = "%s?%s" % (reverse("intake"), querystr)
        return HttpResponseRedirect(intake_url)


class PatientCreate(FormView):
    """A view for creating a new patient using PatientForm."""
    template_name = 'pttrack/intake.html'
    form_class = myforms.PatientForm

    def form_valid(self, form):
        pt = form.save()
        pt.save()
        return HttpResponseRedirect(reverse("demographics-create",
                                            args=(pt.id,)))

    def get_initial(self):
        initial = super(PatientCreate, self).get_initial()


        initial.update(utils.get_names_from_url_query_dict(self.request))
        return initial


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

    redirect_to = request.GET['next']
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = reverse("home")

    if request.POST:
        request.session['clintype_pk'] = request.POST[RADIO_CHOICE_KEY]
        active_provider_type = get_current_provider_type(request)
        request.session['signs_charts'] = active_provider_type.signs_charts
        request.session['staff_view'] = active_provider_type.staff_view

        return HttpResponseRedirect(redirect_to)

    if request.GET:
        role_options = request.user.provider.clinical_roles.all()

        if len(role_options) == 1:
            request.session['clintype_pk'] = role_options[0].pk
            active_provider_type = get_current_provider_type(request)
            request.session['signs_charts'] = active_provider_type.signs_charts
            request.session['staff_view'] = active_provider_type.staff_view
            return HttpResponseRedirect(redirect_to)
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
        lists = [
            {'url': 'filter=unsigned_workup', 'title': "Unsigned Workups",
             'identifier': 'unsignedwu', 'active': True},
            {'url': 'filter=active', 'title': "Active Patients",
             'identifier': 'activept', 'active': False}]

    elif active_provider_type.staff_view:
        title = "Coordinator Tasks"
        lists = [
            {'url': 'filter=active', 'title': "Active Patients",
             'identifier': 'activept', 'active': True},
            {'url': 'filter=ai_priority', 'title':"Priority Action Items",
            'identifier': 'priorityai', 'active': False},
            {'url': 'filter=ai_active', 'title': "Active Action Items",
             'identifier': 'activeai', 'active': False},
            {'url': 'filter=ai_inactive', 'title': "Pending Action Items",
             'identifier': 'pendingai', 'active': False},
            {'url': 'filter=unsigned_workup', 'title': "Unsigned Workups",
             'identifier': 'unsignedwu', 'active': False},
            {'url': 'filter=user_cases', 'title': "My Cases",
             'identifier': 'usercases', 'active': False}
        ]

    else:
        title = "Active Patients"
        lists = [
            {'url': 'filter=active',
             'title': "Active Patients",
             'identifier': 'activept',
             'active': True}]

    api_url = reverse('pt_list_api')[:-1] + '.json/?' # remove last '/' before adding because there no '/' between /api/pt_list and .json, but reverse generates '/api/pt_list/'

    return render(request, 'pttrack/patient_list.html',
                  {'lists': json.dumps(lists),
                   'title': title,
                   'api_url': api_url})


def patient_detail(request, pk):

    pt = get_object_or_404(mymodels.Patient, pk=pk)

    #   Special zipped list of action item types so they can be looped over.
    #   List 1: Labels for the panel objects of the action items
    #   List 2: Action Item lists based on type (active, pending, completed)
    #   List 3: Title labels for the action items
    #   List 4: True and False determines if the link should be for
    #           done_action_item or update_action_item

    active_ais = []
    inactive_ais = []
    done_ais = []

    # Add action items for apps that are turned on in Osler's base settings
    # OSLER_TODO_LIST_MANAGERS contains app names like referral which contain
    # tasks for clinical teams to carry out (e.g., followup with patient)
    for app, model in settings.OSLER_TODO_LIST_MANAGERS:
        ai = apps.get_model(app, model)

        active_ais.extend(ai.objects.get_active(patient=pt))
        inactive_ais.extend(ai.objects.get_inactive(patient=pt))
        done_ais.extend(ai.objects.get_completed(patient=pt))

    # Calculate the total number of action items for this patient,
    # This total includes all apps that that have associated
    # tasks requiring clinical followup (e.g., referral followup request)
    total_ais = len(active_ais) + len(inactive_ais) + len(done_ais)

    zipped_ai_list = zip(['collapse5', 'collapse6', 'collapse7'],
                         [active_ais, inactive_ais, done_ais],
                         ['Active Action Items', 'Pending Action Items',
                         'Completed Action Items'],
                         [True, True, False])

    # Provide referral list for patient page (includes specialty referrals)
    referrals = Referral.objects.filter(
        patient=pt,
        followuprequest__in=FollowupRequest.objects.all()
    )

    # Add FQHC referral status
    # Note it is possible for a patient to have been referred multiple times
    # This creates some strage cases (e.g., first referral was lost to followup
    # but the second one was successful). In these cases, the last referral
    # status becomes the current status
    fqhc_referrals = Referral.objects.filter(patient=pt, kind__is_fqhc=True)
    referral_status_output = Referral.aggregate_referral_status(fqhc_referrals)

    # Pass referral follow up set to page
    referral_followups = PatientContact.objects.filter(patient=pt)
    total_followups = referral_followups.count() + len(pt.followup_set())

    appointments = Appointment.objects \
        .filter(patient=pt) \
        .order_by('clindate', 'clintime')
    # d = collections.OrderedDict()
    # for a in appointments:
    #     if a.clindate in d:
    #         d[a.clindate].append(a)
    #     else:
    #         d[a.clindate] = [a]

    future_date_appointments = appointments.filter(
        clindate__gte=datetime.date.today()).order_by('clindate', 'clintime')
    previous_date_appointments = appointments.filter(
        clindate__lt=datetime.date.today()).order_by('-clindate', 'clintime')

    future_apt = collections.OrderedDict()
    for a in future_date_appointments:
        if a.clindate in future_apt:
            future_apt[a.clindate].append(a)
        else:
            future_apt[a.clindate] = [a]

    previous_apt = collections.OrderedDict()
    for a in previous_date_appointments:
        if a.clindate in previous_apt:
            previous_apt[a.clindate].append(a)
        else:
            previous_apt[a.clindate] = [a]

    zipped_apt_list = zip(
        ['collapse8', 'collapse9'],
        [future_date_appointments, previous_date_appointments],
        ['Future Appointments', 'Past Appointments'],
        [future_apt, previous_apt])

    return render(request,
                  'pttrack/patient_detail.html',
                  {'zipped_ai_list': zipped_ai_list,
                   'total_ais': total_ais,
                   'referral_status': referral_status_output,
                   'referrals': referrals,
                   'referral_followups': referral_followups,
                   'total_followups': total_followups,
                   'patient': pt,
                   'appointments_by_date': future_apt,
                   'zipped_apt_list': zipped_apt_list})


def all_patients(request):
    """
    Query is written to minimize hits to the database; number of db hits can be
        see on the django debug toolbar.
    """
    patient_list = mymodels.Patient.objects.all() \
        .order_by('last_name') \
        .select_related('gender') \
        .prefetch_related('case_managers') \
        .prefetch_related(Prefetch('workup_set', queryset=workupmodels.Workup.objects.order_by('clinic_day__clinic_date'))) \
        .prefetch_related('actionitem_set')

    # Don't know how to prefetch history https://stackoverflow.com/questions/45713517/use-prefetch-related-in-django-simple-history
    # Source code is https://github.com/treyhunner/django-simple-history/blob/master/simple_history/models.py if we want to try to figure out

    return render(request,
                  'pttrack/all_patients.html',
                  {'object_list': patient_list})



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

