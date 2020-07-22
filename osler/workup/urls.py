from django.urls import re_path
from django.views.generic import DetailView

from osler.core.urls import wrap_url
from osler.workup import models
from osler.workup import views

unwrapped_urlconf = [
    re_path(
        r'^new-note/(?P<pt_id>[0-9]+)/$',
        views.new_note_dispatch,
        name='new-note-dispatch'),

    re_path(
        r'^new/(?P<pt_id>[0-9]+)/$',
        views.WorkupCreate.as_view(),
        name='new-workup'),
    re_path(
        r'^(?P<pk>[0-9]+)/$',
        DetailView.as_view(model=models.Workup),
        name='workup'),
    re_path(
        r'^(?P<pk>[0-9]+)/update/$',
        views.WorkupUpdate.as_view(),
        name='workup-update'),
    re_path(
        r'^(?P<pk>[0-9]+)/sign/$',
        views.sign_workup,
        name='workup-sign'),
    re_path(
        r'^(?P<pk>[0-9]+)/error/$',
        views.error_workup,
        name="workup-error"),
    re_path(
        r'^(?P<pk>[0-9]+)/pdf/$',
        views.pdf_workup,
        name="workup-pdf"),

    # PROGRESS NOTES
    re_path(
        r'^(?P<pt_id>[0-9]+)/psychnote/$',
        views.ProgressNoteCreate.as_view(),
        name="new-progress-note"),
    re_path(
        r'^psychnote/update/(?P<pk>[0-9]+)$',
        views.ProgressNoteUpdate.as_view(),
        name="progress-note-update"),
    re_path(
        r'^psychnote/sign/(?P<pk>[0-9]+)$',
        views.sign_progress_note,
        name='progress-note-sign'),
    re_path(
        r'^psychnote/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=models.ProgressNote),
        name="progress-note-detail"),

    re_path(
        r'^(?P<pt_id>[0-9]+)/clindate/$',
        views.ClinicDateCreate.as_view(),
        name="new-clindate"),
    re_path(
        r'^clindates/$',
        views.clinic_date_list,
        name="clindate-list")
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]
