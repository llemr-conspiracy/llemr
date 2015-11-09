from django.conf.urls import url
from pttrack.urls import url_wrap

from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    url(r'^(?P<pt_id>[0-9]+)/followup/(?P<ftype>[\w]+)/$',
        views.FollowupCreate.as_view(),
        name='new-followup'),
    url(r'^(?P<pt_id>[0-9]+)/followup/$',
        views.followup_choice,
        name='followup-choice'),
    url(r'^followup/referral/(?P<pk>[0-9]+)/$',
        views.ReferralFollowupUpdate.as_view(),
        {"model": "Referral"},
        name="followup"),  # parameter 'model' to identify from others w/ name
    url(r'^followup/lab/(?P<pk>[0-9]+)/$',
        views.LabFollowupUpdate.as_view(),
        {"model": "Lab"},
        name="followup"),
    url(r'^followup/vaccine/(?P<pk>[0-9]+)/$',
        views.VaccineFollowupUpdate.as_view(),
        {"model": "Vaccine"},
        name="followup"),
    url(r'^followup/general/(?P<pk>[0-9]+)/$',
        views.GeneralFollowupUpdate.as_view(),
        {"model": "General"},
        name="followup"),
]

urlpatterns = url_wrap(unwrapped_urlconf)