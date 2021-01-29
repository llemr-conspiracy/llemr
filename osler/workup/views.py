from tempfile import TemporaryFile
from xhtml2pdf import pisa

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import (HttpResponseRedirect, HttpResponseServerError,
                         HttpResponse)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.views.generic.edit import FormView
from django.urls import reverse
from django.utils.timezone import now

from osler.core.views import NoteFormView, NoteUpdate
from osler.core.models import Patient, Encounter

from osler.workup import models
from osler.workup import forms

from osler.users.utils import get_active_role, group_has_perm
from osler.users.decorators import active_permission_required

from django.utils.translation import gettext_lazy as _


def new_note_dispatch(request, pt_id):

    note_types = {
        'Standard Medical Note': reverse("new-workup", args=(pt_id,)),
        'Basic Note': reverse("new-basic-note",
                                    args=(pt_id,)),
    }

    if settings.OSLER_DISPLAY_ATTESTABLE_BASIC_NOTE:
        note_types['Attestable Basic Note'] = reverse("new-attestable-basic-note",
                                                                    args=(pt_id,))
                                                    

    return render(request, 'workup/new-note-dispatch.html',
                  {'note_types': note_types})


def basicnote_detail(request, pk, model):

    note = get_object_or_404(model, pk=pk)
    active_role = get_active_role(request)
    can_sign = False
    can_update = False
    attestable = (model == models.AttestableBasicNote)
    title = ""

    if attestable:
        can_sign = note.group_can_sign(active_role)
        can_update = group_has_perm(active_role, 'workup.change_attestablebasicnote')
        title = "Attestable Basic Note"
    else:
        can_update = group_has_perm(active_role, 'workup.change_basicnote')
        title = "Basic Note"

    return render(request,
        'workup/basicnote_detail.html', 
            {
            'note': note,
            'can_sign': can_sign,
            'can_update': can_update,
            'attestable': attestable,
            'title': title
            }
        )


def workup_detail(request, pk):

    # would prefer not to make extra query, but having link to patient
    # detail within template header is useful for clinics
    workup = get_object_or_404(models.Workup, pk=pk)
    patient = workup.patient
    active_role = get_active_role(request)
    can_sign = models.Workup.group_can_sign(active_role)
    can_export_pdf = group_has_perm(active_role, 'workup.export_pdf_Workup')

    return render(request,
        'workup/workup_detail.html', 
            {
            'workup': workup,
            'patient': patient,
            'can_sign': can_sign,
            'can_export_pdf': can_export_pdf,
            'pk': pk,
            }
        )


class WorkupCreate(NoteFormView):
    '''A view for creating a new workup. Checks to see if today is a
    clinic date first, and prompts its creation if none exist.'''
    
    template_name = 'workup/workup_create.html'
    form_class = forms.WorkupForm
    model = models.Workup
    note_type = 'Workup'

    def get_form_kwargs(self):
        kwargs = super(WorkupCreate, self).get_form_kwargs()

        pt_id = self.kwargs['pt_id']
        kwargs['pt'] = get_object_or_404(Patient, pk=pt_id)

        return kwargs

    def get_initial(self):
        initial = super(WorkupCreate, self).get_initial()
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])

        if Encounter.objects.filter(patient=pt, clinic_day=now().date()).exists():
            initial['encounter'] = Encounter.objects.get(patient=pt, clinic_day=now().date())

        initial['ros'] = _(
            "Please UPDATE with pertinent positives and negatives and then delete this line.\n\n"

            "General: \n"
            "Neuro: \n"
            "HEENT: \n" 
            "Cardiovascular: \n" 
            "Pulmonary: \n"
            "GI: \n"
            "GU: \n"
            "Heme: \n" 
            "Skin: \n"
            "Endo: \n"
            "Musculoskeletal: \n"
            "Psychiatric: "
        )

        initial['pe'] = _(
            "Please UPDATE with pertinent findings and then delete this line.\n\n"

            "General: Well-developed, well-nourished, in no apparent distress.\n"
            "HEENT: Head is normocephalic and atraumatic. Extraocular muscles are intact. Pupils are equal, round, and reactive to light. Nares appear normal. Mouth is without lesions. Mucous membranes are moist. Posterior pharynx has no exudate or lesions.\n"
            "Neck: Supple. No carotid bruits.  No lymphadenopathy or thyromegaly.\n"
            "Lungs: CTAB with normal equal air movement.\n"
            "Heart: Regular rate and rhythm without murmur.\n"
            "Abdomen: Soft, nontender, nondistended.  Normal bowel sounds. No hepatosplenomegaly.\n"
            "Extremities: No cyanosis, clubbing, or edema.\n"
            "Neurologic: Alert and oriented to person, place, time, and situation. CN II through XII are grossly intact.\n"
            "Psychiatric: Normal affect. Denies suicidal or homicidal ideations.\n"
            "Skin: Intact with no rashes. Normal skin turgor. Brisk capillary refill."
        )

        wu_previous = pt.latest_workup()
        if wu_previous is not None:
            date_string = wu_previous.written_datetime.strftime("%B %d, %Y")
            for field in settings.OSLER_WORKUP_COPY_FORWARD_FIELDS:
                initial[field] = settings.OSLER_WORKUP_COPY_FORWARD_MESSAGE.\
                    format(date=date_string,
                           contents=getattr(wu_previous, field))
        else:
            if hasattr(pt, 'demographics') and pt.demographics.chronic_conditions.exists():
                conditions = [str(x) for x in pt.demographics.chronic_conditions.all()]
                initial['pmh'] = 'Chronic condition(s): ' + ', '.join(conditions)
            else:
                initial['pmh'] = 'No chronic conditions reported during intake.'

        return initial

    def form_valid(self, form):
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        active_role = get_active_role(self.request)

        wu = form.save(commit=False)
        wu.patient = pt
        wu.author = self.request.user
        wu.author_type = active_role

        if not wu.is_pending and self.model.group_can_sign(active_role):
            wu.sign(self.request.user, active_role)

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
        active_role = get_active_role(self.request)
        wu = get_object_or_404(models.Workup, pk=kwargs['pk'])

        # if it's an attending, we allow updates.  
        if self.model.group_can_sign(active_role) or not wu.signed():
            return super(WorkupUpdate, self).dispatch(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('workup',
                                        args=(kwargs['pk'],)))

    def get_form_kwargs(self):
        kwargs = super(WorkupUpdate, self).get_form_kwargs()

        note = get_object_or_404(models.Workup, pk=self.kwargs['pk'])
        kwargs['pt'] = note.patient
        
        return kwargs

    def get_success_url(self):
        if self.object.is_pending:
            return reverse('core:patient-detail', args=(self.object.patient.id,))
        else:
            return reverse('workup', args=(self.object.id,))


class AttestableBasicNoteCreate(NoteFormView):
    template_name = 'core/form_submission.html'
    form_class = forms.AttestableBasicNoteForm
    note_type = 'Attestable Basic Note'

    def get_form_kwargs(self):
        kwargs = super(AttestableBasicNoteCreate, self).get_form_kwargs()

        pt_id = self.kwargs['pt_id']
        kwargs['pt'] = get_object_or_404(Patient, pk=pt_id)
        
        return kwargs

    def get_initial(self):
        initial = super(AttestableBasicNoteCreate, self).get_initial()

        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        #if encounter for today's clinic day, select as initial
        if Encounter.objects.filter(patient=pt, clinic_day=now().date()).exists():
            initial['encounter'] = Encounter.objects.get(patient=pt, clinic_day=now().date())
        
        return initial

    def form_valid(self, form):
        note = form.save(commit=False)
        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])

        note.patient = pt
        note.author = self.request.user

        active_role = get_active_role(self.request)
        note.author_type = active_role

        if models.AttestableBasicNote.group_can_sign(active_role):
            note.sign(self.request.user, active_role)

        note.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse("core:patient-detail",
                                            args=(note.patient.id,)))


class AttestableBasicNoteUpdate(NoteUpdate):
    template_name = "core/form-update.html"
    model = models.AttestableBasicNote
    form_class = AttestableBasicNoteCreate.form_class
    note_type = AttestableBasicNoteCreate.note_type

    def get_form_kwargs(self):
        kwargs = super(AttestableBasicNoteUpdate, self).get_form_kwargs()

        note = get_object_or_404(models.AttestableBasicNote, pk=self.kwargs['pk'])
        kwargs['pt'] = note.patient
        
        return kwargs

    def get_success_url(self):
        note = self.object
        return reverse("attestable-basic-note-detail", args=(note.id, ))


class BasicNoteCreate(NoteFormView):
    template_name = 'core/form_submission.html'
    form_class = forms.BasicNoteForm
    note_type = 'Basic Note'

    def get_form_kwargs(self):
        kwargs = super(BasicNoteCreate, self).get_form_kwargs()

        pt_id = self.kwargs['pt_id']
        kwargs['pt'] = get_object_or_404(Patient, pk=pt_id)

        return kwargs

    def get_initial(self):
        initial = super(BasicNoteCreate, self).get_initial()

        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        #if encounter for today's clinic day, select as initial
        if Encounter.objects.filter(patient=pt, clinic_day=now().date()).exists():
            initial['encounter'] = Encounter.objects.get(patient=pt, clinic_day=now().date())
        
        return initial

    def form_valid(self, form):
        note = form.save(commit=False)

        note.patient = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        note.author = self.request.user

        active_role = get_active_role(self.request)
        note.author_type = active_role

        note.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse("core:patient-detail",
                                            args=(note.patient.id,)))


class BasicNoteUpdate(NoteUpdate):
    template_name = "core/form-update.html"
    model = models.BasicNote
    form_class = BasicNoteCreate.form_class
    note_type = BasicNoteCreate.note_type

    def get_form_kwargs(self):
        kwargs = super(BasicNoteUpdate, self).get_form_kwargs()

        note = get_object_or_404(models.BasicNote, pk=self.kwargs['pk'])
        kwargs['pt'] = note.patient
        
        return kwargs

    def get_success_url(self):
        note = self.object
        return reverse("basic-note-detail", args=(note.id, ))


class AddendumCreate(NoteFormView):
    template_name = 'core/form_submission.html'
    form_class = forms.AddendumForm
    note_type = 'Addendum'

    def form_valid(self, form):
        note = form.save(commit=False)

        note.workup = get_object_or_404(models.Workup, pk=self.kwargs['wu_id'])
        note.patient = note.workup.patient
        note.author = self.request.user

        if int(self.kwargs['pt_id']) != note.patient.id:
            return HttpResponseServerError(
                'Patient associated with workup does not match supplied patient primary key.')

        active_role = get_active_role(self.request)
        note.author_type = active_role

        note.save()
        form.save_m2m()

        return HttpResponseRedirect(reverse("workup",
                                            args=(self.kwargs['wu_id'],)))


def sign_attestable_note(request, pk, attestable):

    note = get_object_or_404(attestable, pk=pk)
    active_role = get_active_role(request)

    try:
        note.sign(request.user, active_role)
        note.save()
    except ValueError:
        # thrown exception can be ignored since we just redirect back to the
        # workup detail view anyway
        pass

    return HttpResponseRedirect(note.get_absolute_url())


def error_workup(request, pk):

    wu = get_object_or_404(models.Workup, pk=pk)

    # TODO: clearly a template error here.
    return render(request, 'core/workup_error.html', {'workup': wu})


@active_permission_required('workup.export_pdf_Workup', raise_exception=True)
def pdf_workup(request, pk):

    wu = get_object_or_404(models.Workup, pk=pk)

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
        [str(wu.encounter.clinic_day.month).zfill(2),
         str(wu.encounter.clinic_day.day).zfill(2),
         str(wu.encounter.clinic_day.year)])
    filename = ''.join([initials, ' (', formatdate, ')'])

    response = HttpResponse(pdf, 'application/pdf')
    response["Content-Disposition"] = (
        "attachment; filename=%s.pdf" % (filename,))

    return response
