from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponseServerError, \
    HttpResponse
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils.timezone import now
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from pttrack.views import NoteFormView, NoteUpdate, get_current_provider_type
from pttrack.models import Patient, ProviderType

from xhtml2pdf import pisa

from . import models
from . import forms

from tempfile import TemporaryFile


def get_clindates():
    '''Get the clinic dates associated with today.'''
    clindates = models.ClinicDate.objects.filter(
        clinic_date=now().date())
    return clindates


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
        wu_previous = pt.latest_workup()
        if wu_previous is not None:
            date_string = wu_previous.written_datetime.strftime("%B %d, %Y")
            heading_text = "Migrated from previous workup on " + date_string + ". Please delete this heading and modify the following:\n\n"
            initial['PMH_PSH'] = heading_text + wu_previous.PMH_PSH
            initial['fam_hx'] = heading_text + wu_previous.fam_hx
            initial['soc_hx'] = heading_text + wu_previous.soc_hx
            initial['meds'] = heading_text + wu_previous.meds
            initial['allergies'] = heading_text + wu_previous.allergies

        initial['ros'] = "Default: reviewed and negative"
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
        wu.clinic_day = get_clindates()[0]
        if wu.author_type.signs_charts:
            wu.sign(self.request.user, active_provider_type)

        wu.save()

        form.save_m2m()

        return HttpResponseRedirect(reverse("new-action-item", args=(pt.id,)))


class WorkupUpdate(NoteUpdate):
    template_name = "pttrack/form-update.html"
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
    template_name = "pttrack/form-update.html"
    model = models.ProgressNote
    form_class = forms.ProgressNoteForm
    note_type = 'Psych Progress Note'

    def get_success_url(self):
        pnote = self.object
        return reverse("progress-note-detail", args=(pnote.id, ))


class ProgressNoteCreate(NoteFormView):
    template_name = 'pttrack/form_submission.html'
    form_class = forms.ProgressNoteForm
    note_type = 'Psych Progress Note'

    def form_valid(self, form):
        pnote = form.save(commit=False)

        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        pnote.patient = pt
        pnote.author = self.request.user.provider
        pnote.author_type = get_current_provider_type(self.request)

        pnote.save()

        return HttpResponseRedirect(reverse("patient-detail", args=(pt.id,)))


class ClinicDateCreate(FormView):
    '''A view for creating a new ClinicDate. On submission, it redirects to
    the new-workup view.'''
    template_name = 'pttrack/clindate.html'
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


class ClinicDateList(ListView):

    model = models.ClinicDate
    template_name = 'workup/clindate-list.html'

    def get_queryset(self):
        qs = super(ClinicDateList, self).get_queryset()
        qs = qs.prefetch_related('workup_set', 'clinic_type')
        return qs

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


def error_workup(request, pk):

    wu = get_object_or_404(models.Workup, pk=pk)

    # TODO: clearly a template error here.
    return render(request, 'pttrack/workup_error.html', {'workup': wu})


def pdf_workup(request, pk):

    wu = get_object_or_404(models.Workup, pk=pk)
    active_provider_type = get_object_or_404(ProviderType,
                                             pk=request.session['clintype_pk'])

    if active_provider_type.staff_view:
        data = {'workup': wu}

        template = get_template('workup/workup_body.html')
        html  = template.render(data)

        file = TemporaryFile(mode="w+b")
        pisa.CreatePDF(html.encode('utf-8'), dest=file,
                encoding='utf-8')

        file.seek(0)
        pdf = file.read()
        file.close()

        initials = ''.join(name[0].upper() for name in wu.patient.name(reverse=False, middle_short=False).split())
        formatdate = '.'.join([str(wu.clinic_day.clinic_date.month).zfill(2), str(wu.clinic_day.clinic_date.day).zfill(2), str(wu.clinic_day.clinic_date.year)])
        filename = ''.join([initials, ' (', formatdate, ')'])

        response = HttpResponse(pdf, 'application/pdf')
        response["Content-Disposition"] = "attachment; filename=%s.pdf" % (filename,)
        return response

    else:
        return HttpResponseRedirect(reverse('workup',
                                            args=(wu.id,)))
