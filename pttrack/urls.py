from django.conf.urls import url
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from . import models as mymodels
from . import followup_models as fu_models
from . import views

# pylint: disable=I0011

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$',
        views.action_required_patients,
        name="home"),
    url(r'^all/$',
        ListView.as_view(model=mymodels.Patient),
        name="all-patients"),
    url(r'^intake/$', views.PatientCreate.as_view(), name="intake"),
    url(r'^clindate/(?P<pt_id>[0-9]+)/$',
        views.ClinicDateCreate.as_view(),
        name="new-clindate"),
    url(r'^(?P<pk>[0-9]+)/$',
        DetailView.as_view(model=mymodels.Patient),
        name='patient-detail'),

    # PROVIDERS
    url(r'^new-provider/$',
        views.ProviderCreate.as_view(),
        name='new-provider'),

    # WORKUPS
    url(r'^(?P<pt_id>[0-9]+)/workup/$',
        views.WorkupCreate.as_view(),
        name='new-workup'),
    url(r'^workup/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=mymodels.Workup),
        name='workup'),
    url(r'^workup/update/(?P<pk>[0-9]+)$',
        views.WorkupUpdate.as_view(),
        name='workup-update'),
    url(r'^workup/sign/(?P<pk>[0-9]+)$',
        views.sign_workup,
        name='workup-sign'),

    # ACTION ITEMS
    url(r'^(?P<pt_id>[0-9]+)/action-item/$',
        views.ActionItemCreate.as_view(),
        name='new-action-item'),
    url(r'^action-item/(?P<ai_id>[0-9]+)/done$', views.done_action_item,
        name='done-action-item'),
    url(r'^action-item/(?P<ai_id>[0-9]+)/reset$', views.reset_action_item,
        name='reset-action-item'),

    #  FOLLOWUPS
    url(r'^(?P<pt_id>[0-9]+)/followup/(?P<ftype>[\w]+)/$',
        views.FollowupCreate.as_view(),
        name='new-followup'),
    url(r'^(?P<pt_id>[0-9]+)/followup/$',
        views.followup_choice,
        name='followup-choice'),
    url(r'^followup/referral/(?P<pk>[0-9])/$',
        views.ReferralFollowupUpdate.as_view(),
        {"model": "Referral"},
        name="followup"),  # parameter 'model' to identify from others w/ name
    url(r'^followup/lab/(?P<pk>[0-9])/$',
        views.LabFollowupUpdate.as_view(),
        {"model": "Lab"},
        name="followup"),
    url(r'^followup/vaccine/(?P<pk>[0-9])/$',
        views.VaccineFollowupUpdate.as_view(),
        {"model": "Vaccine"},
        name="followup"),
    url(r'^followup/general/(?P<pk>[0-9])/$',
        views.GeneralFollowupUpdate.as_view(),
        {"model": "General"},
        name="followup"),
]
