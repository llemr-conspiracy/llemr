from django.conf.urls import url
from django.views.generic import ListView, DetailView
from . import models as mymodels
from . import followup_models as fu_models
from . import views

# pylint: disable=I0011

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$', ListView.as_view(model=mymodels.Patient,)),
    url(r'^intake/$', views.PatientCreate.as_view(), name="intake"),
    url(r'^clindate/(?P<pt_id>[0-9]+)/$',
        views.ClinicDateCreate.as_view(),
        name="new-clindate"),
    url(r'^(?P<pk>[0-9]+)/$',
        DetailView.as_view(model=mymodels.Patient),
        name='patient-detail'),
    url(r'^(?P<pt_id>[0-9]+)/followup/(?P<ftype>[\w]+)/$',
        views.FollowupCreate.as_view(),
        name='new-followup'),
    url(r'^(?P<pt_id>[0-9]+)/followup/$',
        views.workup_choice,
        name='followup-choice'),
    url(r'^(?P<pt_id>[0-9]+)/workup/$',
        views.WorkupCreate.as_view(), name='new-workup'),
    url(r'^(?P<pt_id>[0-9]+)/action-item/$', views.ActionItemCreate.as_view(),
        name='new-action-item'),
    url(r'^workup/(?P<pk>[0-9]+)$', DetailView.as_view(model=mymodels.Workup),
        name='workup'),
    url(r'^action-item/(?P<ai_id>[0-9]+)/done$', views.done_action_item,
        name='done-action-item'),
    url(r'^action-item/(?P<ai_id>[0-9]+)/reset$', views.reset_action_item,
        name='reset-action-item'),
    url(r'^$', DetailView.as_view(model=mymodels.Workup,)),

    url(r'^followup/(?P<pk>[0-9])/$',
        views.ReferralFollowupUpdate.as_view(),
        {"model": "Referral"},
        name="followup"),
    url(r'^followup/(?P<pk>[0-9])/$',
        DetailView.as_view(model=fu_models.LabFollowup),
        {"model": "Lab"},
        name="followup"),
]
