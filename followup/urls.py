from django.conf.urls import url
from pttrack.urls import wrap_url

from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    url(r'^(?P<pt_id>[0-9]+)/referral/$',
        views.ReferralFollowupCreate.as_view(),
        name='new-referral-followup'),
    url(r'^(?P<pt_id>[0-9]+)/(?P<ftype>[\w]+)/$',
        views.FollowupCreate.as_view(),
        name='new-followup'),
    url(r'^(?P<pt_id>[0-9]+)/$',
        views.followup_choice,
        name='followup-choice'),
    url(r'^referral/(?P<pk>[0-9]+)/$',
        views.ReferralFollowupUpdate.as_view(),
        {"model": "Referral"},
        name="followup"),  # parameter 'model' to identify from others w/ name
    url(r'^lab/(?P<pk>[0-9]+)/$',
        views.LabFollowupUpdate.as_view(),
        {"model": "Lab"},
        name="followup"),
    url(r'^vaccine/(?P<pk>[0-9]+)/$',
        views.VaccineFollowupUpdate.as_view(),
        {"model": "Vaccine"},
        name="followup"),
    url(r'^general/(?P<pk>[0-9]+)/$',
        views.GeneralFollowupUpdate.as_view(),
        {"model": "General"},
        name="followup"),
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]