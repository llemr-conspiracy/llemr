from __future__ import unicode_literals
from django.urls import re_path
from pttrack.urls import wrap_url

from . import views
from . import models

unwrapped_urlconf = [  # pylint: disable=invalid-name
    re_path(
        r'^new-referral/(?P<pt_id>[0-9]+)/(?P<rtype>[-a-z]+)$',
        views.ReferralCreate.as_view(),
        name='new-referral'),
    re_path(
        r'^followup-request/(?P<pt_id>[0-9]+)/(?P<referral_id>[0-9]+)$',
        views.FollowupRequestCreate.as_view(),
        name='new-followup-request'),
    re_path(
        r'^patient-contact/(?P<pt_id>[0-9]+)/(?P<referral_id>[0-9]+)/'
        r'(?P<followup_id>[0-9]+)$',
        views.PatientContactCreate.as_view(),
        name=models.FollowupRequest.MARK_DONE_URL_NAME),
    re_path(
        r'^select-referral/(?P<pt_id>[0-9]+)$',
        views.select_referral,
        name='select-referral'),
    re_path(
        r'^select-referral-type/(?P<pt_id>[0-9]+)$',
        views.select_referral_type,
        name='select-referral-type')
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]
