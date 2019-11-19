from django.conf.urls import url
from pttrack.urls import wrap_url
from django.views.generic import DetailView

from . import models
from . import views

unwrapped_urlconf = [
    url(r'^new-note/(?P<pt_id>[0-9]+)/$',
        views.new_note_dispatch,
        name='new-note-dispatch'),

    url(r'^new/(?P<pt_id>[0-9]+)/$',
        views.WorkupCreate.as_view(),
        name='new-workup'),
    url(r'^(?P<pk>[0-9]+)/$',
        DetailView.as_view(model=models.Workup),
        name='workup'),
    url(r'^(?P<pk>[0-9]+)/update/$',
        views.WorkupUpdate.as_view(),
        name='workup-update'),
    url(r'^(?P<pk>[0-9]+)/sign/$',
        views.sign_workup,
        name='workup-sign'),
    url(r'^(?P<pk>[0-9]+)/error/$',
        views.error_workup,
        name="workup-error"),
    url(r'^(?P<pk>[0-9]+)/pdf/$',
        views.pdf_workup,
        name="workup-pdf"),

    # Psych NOTES
    url(r'^(?P<pt_id>[0-9]+)/psychnote/$',
        views.PsychNoteCreate.as_view(),
        name="new-psych-note"),
    url(r'^psychnote/update/(?P<pk>[0-9]+)$',
        views.PsychNoteUpdate.as_view(),
        name="psych-note-update"),
    url(r'^psychnote/sign/(?P<pk>[0-9]+)$',
        views.sign_psych_note,
        name='psych-note-sign'),
    url(r'^psychnote/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=models.PsychNote),
        name="psych-note-detail"),

    # Progress NOTES
    url(r'^(?P<pt_id>[0-9]+)/progressnote/$',
        views.ProgressNoteCreate.as_view(),
        name="new-progress-note"),
    url(r'^progressnote/update/(?P<pk>[0-9]+)$',
        views.ProgressNoteUpdate.as_view(),
        name="progress-note-update"),
    url(r'^progressnote/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=models.ProgressNotes),
        name="progress-note-detail"),

    url(r'^(?P<pt_id>[0-9]+)/clindate/$',
        views.ClinicDateCreate.as_view(),
        name="new-clindate"),
    url(r'^clindates/$',
        views.clinic_date_list,
        name="clindate-list")
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]
