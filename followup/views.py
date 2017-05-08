from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from pttrack.models import Patient
from pttrack.views import NoteUpdate, NoteFormView, get_current_provider_type

from . import forms
from . import models


def followup_choice(request, pt_id):
    '''Prompt the user to choose a follow up type.'''
    pt = get_object_or_404(Patient, pk=pt_id)
    return render(request, 'pttrack/followup-choice.html', {'patient': pt})


class FollowupUpdate(NoteUpdate):
    template_name = "pttrack/form-update.html"

    def get_success_url(self):
        pt = self.object.patient
        return reverse("patient-detail", args=(pt.id, ))


class ReferralFollowupUpdate(FollowupUpdate):
    model = models.ReferralFollowup
    form_class = forms.ReferralFollowup
    note_type = "Referral Followup"


class LabFollowupUpdate(FollowupUpdate):
    model = models.LabFollowup
    form_class = forms.LabFollowup
    note_type = "Lab Followup"


class VaccineFollowupUpdate(FollowupUpdate):
    model = models.VaccineFollowup
    form_class = forms.VaccineFollowup
    note_type = "Vaccine Followup"


class GeneralFollowupUpdate(FollowupUpdate):
    model = models.GeneralFollowup
    form_class = forms.GeneralFollowup
    note_type = "General Followup"


class FollowupCreate(NoteFormView):
    '''A view for creating a new Followup'''
    template_name = 'pttrack/form_submission.html'
    note_type = "Followup"

    def get_form_class(self, **kwargs):

        ftype = self.kwargs['ftype']

        futypes = {'labs': forms.LabFollowup,
                   'vaccine': forms.VaccineFollowup,
                   'general': forms.GeneralFollowup}

        return futypes[ftype]

    def get_followup_model(self):
        '''Get the subtype of Followup model used by the FollowupForm used by
        this FollowupCreate view.'''
        # I have no idea if this is the right way to do this. It seems a bit
        # dirty.
        return self.get_form_class().Meta.model

    def form_valid(self, form):

        pt = get_object_or_404(Patient, pk=self.kwargs['pt_id'])
        fu = form.save(commit=False)
        fu.patient = pt
        fu.author = self.request.user.provider
        fu.author_type = get_current_provider_type(self.request)

        fu.save()

        form.save_m2m()

        if 'followup_create' in self.request.POST:
            return HttpResponseRedirect(reverse('new-action-item',
                                                args=(pt.id,)))
        else:
            return HttpResponseRedirect(reverse("patient-detail",
                                                args=(pt.id,)))


class ReferralFollowupCreate(FollowupCreate):
    '''A view for creating a new ReferralFollowup'''
    template_name = 'followup/referral-followup-create.html'
    form_class = forms.ReferralFollowup

    def get_form_class(self, **kwargs):
        return self.form_class
