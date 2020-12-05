from builtins import zip
import collections
import datetime

from django.conf import settings
from django.apps import apps
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Prefetch, FilteredRelation, Q
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.timezone import now

from osler.workup import models as workupmodels
from osler.referral.models import Referral, FollowupRequest, PatientContact
from osler.vaccine.models import VaccineFollowup
from osler.appointment.models import Appointment

from osler.core import models as core_models
from osler.core import forms
from osler.core import utils

from osler.users.utils import get_active_role, group_has_perm

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from django.db.models.fields.related import ManyToManyField

class NoteFormView(FormView):
    note_type = None

    def get_context_data(self, **kwargs):
        '''Inject self.note_type and patient into the context.'''

        if self.note_type is None:
            raise ImproperlyConfigured("NoteCreate view must have"
                                       "'note_type' variable set.")

        context = super(NoteFormView, self).get_context_data(**kwargs)
        context['note_type'] = self.note_type

        if 'pt_id' in self.kwargs:
            context['patient'] = core_models.Patient.objects. \
                get(pk=self.kwargs['pt_id'])

        return context


class NoteUpdate(UpdateView):
    note_type = None

    def get_context_data(self, **kwargs):
        """Inject self.note_type as the note type."""

        if self.note_type is None:
            raise ImproperlyConfigured("NoteUpdate view must have"
                                       "'note_type' variable set.")

        context = super(NoteUpdate, self).get_context_data(**kwargs)
        context['note_type'] = self.note_type

        return context

    # TODO: add shared form_valid code here from all subclasses.


class UserInit(FormView):
    '''A view for filling in the Person details and groups for a User'''
    template_name = 'core/user_init.html'
    form_class = forms.UserInitForm

    def get_initial(self):
        initial = super(UserInit, self).get_initial()
        user = self.request.user
        for field in self.form_class.Meta.fields:
            initial[field] = getattr(user, field)
        return initial

    def form_valid(self, form):
        user = self.request.user
        User = get_user_model()
        for field in self.form_class.Meta.fields:
            field_class = getattr(User, field).field
            value = form.cleaned_data[field]
            # many to many relations need to use set()
            if isinstance(field_class, ManyToManyField):
                getattr(user, field).set(value)
            else:
                setattr(user, field, value)
        user.save()

        if 'next' in self.request.GET:
            next_url = self.request.GET['next']
        else:
            next_url = reverse('home')

        return HttpResponseRedirect(next_url)

    def get_context_data(self, **kwargs):
        context = super(UserInit, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next')
        return context


class ActionItemCreate(NoteFormView):
    """A view for creating ActionItems using the ActionItemForm."""
    template_name = 'core/form_submission.html'
    form_class = forms.ActionItemForm
    note_type = 'Action Item'

    def form_valid(self, form):
        '''Set the patient, user, and written timestamp for the item.'''
        pt = get_object_or_404(core_models.Patient, pk=self.kwargs['pt_id'])
        ai = form.save(commit=False)

        ai.completion_date = None
        ai.author = self.request.user
        ai.author_type = get_active_role(self.request)
        ai.patient = pt

        ai.save()

        return HttpResponseRedirect(reverse("core:patient-detail",
                                            args=(pt.id,)))


class ActionItemUpdate(NoteUpdate):
    template_name = "core/form-update.html"
    model = core_models.ActionItem
    form_class = forms.ActionItemForm
    note_type = "Action Item"

    def get_success_url(self):
        pt = self.object.patient
        return reverse("core:patient-detail", args=(pt.id, ))


class PatientUpdate(UpdateView):
    template_name = 'core/patient-update.html'
    model = core_models.Patient
    form_class = forms.PatientForm

    def form_valid(self, form):
        pt = form.save()
        pt.save()

        return HttpResponseRedirect(reverse("core:patient-detail",
                                            args=(pt.id,)))


class PreIntakeSelect(ListView):
    """Allows users to see all patients with similar name to a
    particular patient first and last name. Allows user to open one of
    the similarly named patients, or create a new patient
    """
    template_name = 'core/preintake-select.html'
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
            reverse("core:intake"),
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

    template_name = 'core/preintake.html'
    form_class = forms.DuplicatePatientForm

    def form_valid(self, form):
        first_name_str = form.cleaned_data['first_name'].capitalize()
        last_name_str = form.cleaned_data['last_name'].capitalize()
        matching_patients = utils.return_duplicates(first_name_str,
                                                    last_name_str)

        querystr = '%s=%s&%s=%s' % ("first_name", first_name_str,
                                    "last_name", last_name_str)
        if len(matching_patients) > 0:
            intake_url = "%s?%s" % (reverse("core:preintake-select"), querystr)
            return HttpResponseRedirect(intake_url)

        intake_url = "%s?%s" % (reverse("core:intake"), querystr)
        return HttpResponseRedirect(intake_url)


class PatientCreate(FormView):
    """A view for creating a new patient using PatientForm."""
    template_name = 'core/intake.html'
    form_class = forms.PatientForm

    def form_valid(self, form):
        pt = form.save()
        pt.save()
        return HttpResponseRedirect(reverse("demographics-create",
                                            args=(pt.id,)))

    def get_initial(self):
        initial = super(PatientCreate, self).get_initial()
        initial.update(utils.get_names_from_url_query_dict(self.request))

        initial['city'] = settings.OSLER_DEFAULT_CITY
        initial['state'] = settings.OSLER_DEFAULT_STATE
        initial['zip_code'] = settings.OSLER_DEFAULT_ZIP_CODE
        initial['country'] = settings.OSLER_DEFAULT_COUNTRY

        return initial


class DocumentUpdate(NoteUpdate):
    template_name = "core/form-update.html"
    model = core_models.Document
    form_class = forms.DocumentForm
    note_type = "Document"

    def get_success_url(self):
        doc = self.object
        return reverse("core:document-detail", args=(doc.id, ))


class DocumentCreate(NoteFormView):
    '''A view for uploading a document'''
    template_name = 'core/form_submission.html'
    form_class = forms.DocumentForm
    note_type = 'Document'

    def form_valid(self, form):
        doc = form.save(commit=False)

        pt = get_object_or_404(core_models.Patient, pk=self.kwargs['pt_id'])
        doc.patient = pt
        doc.author = self.request.user
        doc.author_type = get_active_role(self.request)

        doc.save()

        return HttpResponseRedirect(reverse("core:patient-detail",
                                            args=(pt.id,)))


def choose_role(request):
    RADIO_CHOICE_KEY = 'radio-roles'

    redirect_to = request.GET['next']
    if not url_has_allowed_host_and_scheme(url=redirect_to,
                                           allowed_hosts=request.get_host()):
        redirect_to = reverse('home')

    if request.POST:
        active_role_pk = request.POST[RADIO_CHOICE_KEY]
        request.session['active_role_pk'] = active_role_pk
        request.session['active_role_name'] = Group.objects.get(pk=active_role_pk).name

        return HttpResponseRedirect(redirect_to)

    if request.GET:
        role_options = request.user.groups.all()
        if len(role_options) == 1:
            active_role_pk = role_options[0].pk
            request.session['active_role_pk'] = active_role_pk
            request.session['active_role_name'] = Group.objects.get(pk=active_role_pk).name

            return HttpResponseRedirect(redirect_to)
        elif not role_options:
            return HttpResponseServerError(
                "Fatal: This user must be initialized with groups. Report this error!")
        else:
            return render(request, 'core/role_choice.html',
                          {'roles': role_options,
                           'choice_key': RADIO_CHOICE_KEY})


def home_page(request):
    return HttpResponseRedirect(reverse(settings.OSLER_DEFAULT_DASHBOARD))


def patient_detail(request, pk):

    pt = get_object_or_404(core_models.Patient, pk=pk)

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

    zipped_ai_list = list(zip(
        ['collapse8', 'collapse9', 'collapse10'],
        [active_ais, inactive_ais, done_ais],
        ['Active Action Items', 'Pending Action Items',
         'Completed Action Items'],
        [True, True, False]))

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
    #Pass vaccine follow up set to page
    vaccine_followups = VaccineFollowup.objects.filter(patient=pt)
    total_followups = referral_followups.count() + len(pt.followup_set()) + vaccine_followups.count()

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

    zipped_apt_list = list(zip(
        ['collapse11', 'collapse12'],
        [future_date_appointments, previous_date_appointments],
        ['Future Appointments', 'Past Appointments'],
        [future_apt, previous_apt]))

    # Permissions to display things on patient-detail, just toggle active status for now
    # But I think this way vs in the html will make it easier to add/change later
    active_role = get_active_role(request)
    can_activate = pt.group_can_activate(active_role)
    can_case_manage = group_has_perm(active_role, 'core.case_manage_Patient')
    can_export_pdf = group_has_perm(active_role, 'workup.export_pdf_Workup')

    context = {
        'zipped_ai_list': zipped_ai_list,
        'total_ais': total_ais,
        'referral_status': referral_status_output,
        'referrals': referrals,
        'referral_followups': referral_followups,
        'vaccine_followups': vaccine_followups,
        'total_followups': total_followups,
        'patient': pt,
        'appointments_by_date': future_apt,
        'zipped_apt_list': zipped_apt_list,
        'can_activate': can_activate,
        'can_case_manage': can_case_manage,
        'can_export_pdf': can_export_pdf
    }

    return render(request,
        'core/patient_detail.html',
        context)


def all_patients(request, title='All Patients', active=False):
    """
    Query is written to minimize hits to the database; number of db hits can be
        see on the django debug toolbar.
    """
    patient_list = core_models.Patient.objects.all()
    if active:
        #if a patient has two open encounters, they will appear twice because of 
        #ordering by encounter, distinct() doesn't work
        #I decided was ok because you should be inactivating encounters
        patient_list = core_models.Patient.objects.filter(encounter__status__is_active=True)\
            .order_by('encounter__order')
    
    patient_list = patient_list \
        .select_related('gender') \
        .prefetch_related('case_managers') \
        .prefetch_related('workup_set') \
        .prefetch_related('actionitem_set')

    # Don't know how to prefetch history
    # https://stackoverflow.com/questions/45713517/use-prefetch-related-in-django-simple-history
    # Source code is https://github.com/treyhunner/django-simple-history/blob/master/simple_history/models.py if we want to try to figure out

    return render(request,
                  'core/all_patients.html',
                  {
                    'object_list': patient_list,
                    'title': title
                  })


def get_clindates():
    '''Get the clinic dates associated with today.'''
    clindates = workupmodels.ClinicDate.objects.filter(
        clinic_date=now().date())
    return clindates


def get_or_create_encounter(pt_id, clinic_id):
    '''Returns 1 active encounter associated with this pt and clindate'''
    encounter, created = core_models.Encounter.objects.get_or_create(patient=pt_id, clinic_day=clinic_id,
        defaults={'status': core_models.default_active_status()})
    return encounter


def patient_activate_detail(request, pk):
    '''Toggle status to default active/inactive'''
    pt = get_object_or_404(core_models.Patient, pk=pk)
    active_role = get_active_role(request)

    can_activate = pt.group_can_activate(active_role)

    if can_activate:
        #moved out of core/models because needed all this stuff
        if pt.get_status().is_active:
            encounter = pt.last_encounter()
            encounter.status = core_models.default_inactive_status()
            encounter.save()
        else: #if pt is inactive, will need to make new active encounter
            clindates = get_clindates()
            if len(clindates) == 0:
                #dispatch to ClinicDateCreate because the ClinicDate for today doesn't exist
                #after making the ClinicDate will auto make new encounter for this pt
                return HttpResponseRedirect(reverse("new-clindate", args=(pt.id,)))
            elif len(clindates) == 1:
                #ClinicDate exists so make new active encounter or activate existing one for today
                encounter = get_or_create_encounter(pt, clindates[0])
                if not encounter.status.is_active:
                    encounter.status = core_models.default_active_status()
                    encounter.save()
            else:  # we have >1 clindate today.
                return HttpResponseServerError(
                    'There are two or more "clinic day" entries in the database '
                    'for today. Since notes are associated with one and only one '
                    'clinic day, one clinic day has to be deleted. This can be '
                    'done in the admin panel by a user with sufficient ',
                    'privileges (e.g. coordinator).')
    else:
        raise ValueError("Special permissions are required to change active status.")

    return HttpResponseRedirect(reverse("core:patient-detail", args=(pt.id,)))


def patient_activate_home(request, pk):
    pt = get_object_or_404(core_models.Patient, pk=pk)
    active_role = get_active_role(request)

    can_activate = pt.group_can_activate(active_role)

    if can_activate:
        pt.toggle_active_status(request.user, active_role)

    pt.save()

    return HttpResponseRedirect(reverse("home"))


def done_action_item(request, ai_id):
    ai = get_object_or_404(core_models.ActionItem, pk=ai_id)
    ai.mark_done(request.user)
    ai.save()

    if settings.OSLER_DISPLAY_FOLLOWUP:
        return HttpResponseRedirect(reverse("new-actionitem-followup",
                                        kwargs={'pt_id':ai.patient.pk,
                                        'ai_id':ai.pk}))
    else:
        return HttpResponseRedirect(reverse("core:patient-detail",
                                        args=(ai.patient.pk,)))


def reset_action_item(request, ai_id):
    ai = get_object_or_404(core_models.ActionItem, pk=ai_id)
    ai.clear_done()
    ai.save()
    return HttpResponseRedirect(reverse("core:patient-detail",
                                        args=(ai.patient.id,)))
