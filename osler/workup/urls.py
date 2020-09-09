from functools import partial

from django.urls import re_path
from django.views.generic import DetailView

from osler.core.urls import wrap_url
from osler.workup import models
from osler.workup import views

unwrapped_urlconf = [

    # DISPATCH
    re_path(
        r'^new-note/(?P<pt_id>[0-9]+)/$',
        views.new_note_dispatch,
        name='new-note-dispatch'),

    # WORKUPS
    re_path(
        r'^new/(?P<pt_id>[0-9]+)/$',
        views.WorkupCreate.as_view(),
        name='new-workup'),
    re_path(
        r'^(?P<pk>[0-9]+)/$',
        views.workup_detail,
        name='workup'),
    re_path(
        r'^(?P<pk>[0-9]+)/update/$',
        views.WorkupUpdate.as_view(),
        name='workup-update'),
    re_path(
        r'^(?P<pk>[0-9]+)/sign/$',
        partial(views.sign_attestable_note, attestable=models.Workup),
        name='workup-sign'),
    re_path(
        r'^(?P<pk>[0-9]+)/error/$',
        views.error_workup,
        name="workup-error"),
    re_path(
        r'^(?P<pk>[0-9]+)/pdf/$',
        views.pdf_workup,
        name="workup-pdf"),

    # ATTESTABLE BASIC NOTES
    re_path(
        r'^(?P<pt_id>[0-9]+)/attestable-basic-note/$',
        views.AttestableBasicNoteCreate.as_view(),
        name="new-attestable-basic-note"),
    re_path(
        r'^attestable-basic-note/update/(?P<pk>[0-9]+)/$',
        views.AttestableBasicNoteUpdate.as_view(),
        name="attestable-basic-note-update"),
    re_path(
        r'^attestable-basic-note/sign/(?P<pk>[0-9]+)/$',
        partial(views.sign_attestable_note, attestable=models.AttestableBasicNote),
        name='attestable-basic-note-sign'),
    re_path(
        r'^attestable-basic-note/(?P<pk>[0-9]+)/$',
        partial(views.basicnote_detail, model=models.AttestableBasicNote),
        name="attestable-basic-note-detail"),

    # BASIC NOTES
    re_path(
        r'^(?P<pt_id>[0-9]+)/basic-note/$',
        views.BasicNoteCreate.as_view(),
        name="new-basic-note"),
    re_path(
        r'^basic-note/update/(?P<pk>[0-9]+)/$',
        views.BasicNoteUpdate.as_view(),
        name="basic-note-update"),
    re_path(
        r'^basic-note/(?P<pk>[0-9]+)/$',
        partial(views.basicnote_detail, model=models.BasicNote),
        name="basic-note-detail"),

    # CLINIC DATES
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
