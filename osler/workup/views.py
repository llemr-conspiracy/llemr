from tempfile import TemporaryFile
from xhtml2pdf import pisa

from django.shortcuts import get_object_or_404, render
from django.http import (HttpResponseRedirect, HttpResponseServerError,
                         HttpResponse)
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template
from django.utils.timezone import now
from django.views.generic.edit import FormView
from django.conf import settings

from osler.core.views import (NoteFormView, NoteUpdate,
                                 get_current_provider_type)
from osler.core.models import Patient, ProviderType

from osler.workup import models
from osler.workup import forms


def get_clindates():
    '''Get the clinic dates associated with today.'''
    clindates = models.ClinicDate.objects.filter(
        clinic_date=now().date())
    return clindates


def new_note_dispatch(request, pt_id):

    note_types = {
        'Standard Note': reverse("new-workup", args=(pt_id,)),
        'Clinical Psychology Note': reverse("new-progress-note",
                                            args=(pt_id,)),
    }

    return render(request, 'workup/new-note-dispatch.html',
                  {'note_types': note_types})


class WorkupCreate(NoteFormView):
    '''A view for creating a new workup. Checks to see if today is a
    clinic date first, and prompts its creation if none exist.'''
    template_name = 'workup/workup-create.html'
    form_class = forms.WorkupForm
    note_type = 'Workup'

    def get(self, *args, **kwargs):
        """Check that we have an instantiated ClinicDate today,
        then dispatch to get() of the superclass view."""

        clindates = get_clindates()
        pt = get_object_or_404(Patient, pk=kwargs['pt_id'])

        if len(clindates) == 0:
            # dispatch to ClinicDateCreate because the ClinicDate doesn't exist
            return HttpResponseRedirect(reverse("new-clindate", args=(pt.id,)))
        elif len(clindates) == 1:
            # dispatch to our own view, since we know there's a ClinicDate
            # for today
            kwargs['pt_id'] = pt.id
            return super(WorkupCreate,
                         self).get(self, *args, **kwargs)
        else:  # we have >1 clindate today.
            return HttpResponseServerError(
                'There are two or more "clinic day" entries in the database '
                'for today. Since notes are associated with one and only one '
                'clinic day, one clinic day has to be deleted. This can be '
                'done in the admin panel by a user with sufficient ',
                'privileges (e.g. coordinator).')

    def get_initial(self):
        initial = super(WorkupCreate, self).get_initial()
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])

        # self.get() checks for >= 1 ClinicDay
        initial['clinic_day'] = get_clindates().first()
        initial['ros'] = "Default: reviewed and negative"

        wu_previous = pt.latest_workup()
        if wu_previous is not None:
            date_string = wu_previous.written_datetime.strftime("%B %d, %Y")
            for field in settings.OSLER_WORKUP_COPY_FORWARD_FIELDS:
                initial[field] = settings.OSLER_WORKUP_COPY_FORWARD_MESSAGE.\
                    format(date=date_string,
                           contents=getattr(wu_previous, field))

        return initial

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        active_provider_type = get_object_or_404(
            ProviderType,
            pk=self.request.session['clintype_pk'])

        wu = form.save(commit=False)
        wu.patient = pt
        wu.author = self.request.user.provider
        wu.author_type = get_current_provider_type(self.request)
        if wu.author_type.signs_charts:
            wu.sign(self.request.user, active_provider_type)

        wu.save()

        form.save_m2m()

        return HttpResponseRedirect(reverse("core:patient-detail", args=(pt.id,)))


class WorkupUpdate(NoteUpdate):
    template_name = "core/form-update.html"
    model = models.Workup
    form_class = forms.WorkupForm
    note_type = "Workup"

    def dispatch(self, *args, **kwargs):
        '''
        Intercept dispatch for NoteUpdate and verify that the user has
        permission to modify this Workup.
        '''
        current_user_type = get_current_provider_type(self.request)
        wu = get_object_or_404(models.Workup, pk=kwargs['pk'])

        # if it's an attending, we allow updates.
        if current_user_type.signs_charts or not wu.signed():
            return super(WorkupUpdate, self).dispatch(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('workup',
                                        args=(kwargs['pk'],)))

    def get_success_url(self):
        return reverse('workup', args=(self.object.id,))


class ProgressNoteUpdate(NoteUpdate):
    template_name = "core/form-update.html"
    model = models.ProgressNote
    form_class = forms.ProgressNoteForm
    note_type = 'Clinical Psychology Note'

    def get_success_url(self):
        pnote = self.object
        return reverse("progress-note-detail", args=(pnote.id, ))


class ProgressNoteCreate(NoteFormView):
    template_name = 'core/form_submission.html'
    form_class = forms.ProgressNoteForm
    note_type = 'Clinical Psychology Note'

    def form_valid(self, form):
        pnote = form.save(commit=False)
        active_provider_type = get_object_or_404(
            ProviderType,
            pk=self.request.session['clintype_pk'])
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        pnote.patient = pt
        pnote.author = self.request.user.provider
        pnote.author_type = get_current_provider_type(self.request)
        if pnote.author_type.signs_charts:
            pnote.sign(self.request.user, active_provider_type)
        pnote.save()

        form.save_m2m()

        return HttpResponseRedirect(reverse("core:patient-detail", args=(pt.id,)))


class ClinicDateCreate(FormView):
    '''A view for creating a new ClinicDate. On submission, it redirects to
    the new-workup view.'''
    template_name = 'core/clindate.html'
    form_class = forms.ClinicDateForm

    def form_valid(self, form):
        '''Add today's date to the ClinicDate form and submit the form.'''

        # determine from our URL which patient we wanted to work up before we
        # got redirected to create a clinic date
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])

        # if there's already a clindate for today, redirect to workup create
        if len(get_clindates()) == 0:
            clindate = form.save(commit=False)

            today = now().date()
            clindate.clinic_date = today
            clindate.save()

        return HttpResponseRedirect(reverse("new-workup", args=(pt.id,)))


def clinic_date_list(request):

    qs = models.ClinicDate.objects.prefetch_related(
        'workup_set',
        'clinic_type',
        'workup_set__attending',
        'workup_set__signer',
    )

    paginator = Paginator(qs, per_page=10)
    page = request.GET.get('page')

    try:
        clinic_days = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        clinic_days = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        clinic_days = paginator.page(paginator.num_pages)

    return render(request, 'workup/clindate-list.html',
                  {'object_list': clinic_days,
                   'page_range': paginator.page_range})


def sign_workup(request, pk):

    wu = get_object_or_404(models.Workup, pk=pk)
    active_provider_type = get_object_or_404(ProviderType,
                                             pk=request.session['clintype_pk'])

    try:
        wu.sign(request.user, active_provider_type)
        wu.save()
    except ValueError:
        # thrown exception can be ignored since we just redirect back to the
        # workup detail view anyway
        pass

    return HttpResponseRedirect(reverse("workup", args=(wu.id,)))


def sign_progress_note(request, pk):
    wu = get_object_or_404(models.ProgressNote, pk=pk)
    active_provider_type = get_object_or_404(ProviderType,
                                             pk=request.session['clintype_pk'])
    try:
        wu.sign(request.user, active_provider_type)
        wu.save()
    except ValueError:
        # thrown exception can be ignored since we just redirect back to the
        # workup detail view anyway
        pass

    return HttpResponseRedirect(reverse("progress-note-detail", args=(wu.id,)))

def error_workup(request, pk):

    wu = get_object_or_404(models.Workup, pk=pk)

    # TODO: clearly a template error here.
    return render(request, 'core/workup_error.html', {'workup': wu})


def pdf_workup(request, pk):

    wu = get_object_or_404(models.Workup, pk=pk)
    active_provider_type = get_object_or_404(ProviderType,
                                             pk=request.session['clintype_pk'])

    if active_provider_type.staff_view:
        data = {'workup': wu}

        template = get_template('workup/workup_body.html')
        html = template.render(data)

        with TemporaryFile(mode="w+b") as file:
            pisa.CreatePDF(html.encode('utf-8'), dest=file,
                           encoding='utf-8')

            file.seek(0)
            pdf = file.read()

        initials = ''.join(name[0].upper() for name in wu.patient.name(
            reverse=False, middle_short=False).split())
        formatdate = '.'.join(
            [str(wu.clinic_day.clinic_date.month).zfill(2),
             str(wu.clinic_day.clinic_date.day).zfill(2),
             str(wu.clinic_day.clinic_date.year)])
        filename = ''.join([initials, ' (', formatdate, ')'])

        response = HttpResponse(pdf, 'application/pdf')
        response["Content-Disposition"] = (
            "attachment; filename=%s.pdf" % (filename,))

        return response
    else:
        return HttpResponseRedirect(reverse('workup',
                                            args=(wu.id,)))
