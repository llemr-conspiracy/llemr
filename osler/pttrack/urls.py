from __future__ import unicode_literals
from django.urls import re_path
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

from django.contrib.auth.decorators import login_required
from .decorators import provider_required, clintype_required, \
    provider_update_required
from . import models
from . import views

# pylint: disable=I0011

unwrapped_urlpatterns = [  # pylint: disable=invalid-name
    re_path(
        r'^$',
        views.home_page,
        name="home"),
    re_path(
        r'^all/$',
        views.all_patients,
        name="all-patients"),
    re_path(
        r'^preintake-select/$',
        views.PreIntakeSelect.as_view(),
        name="preintake-select"),
    re_path(
        r'^preintake/$',
        views.PreIntake.as_view(),
        name="preintake"),
    re_path(
        r'^intake/$',
        views.PatientCreate.as_view(),
        name="intake"),
    re_path(
        r'^(?P<pk>[0-9]+)/$',
        views.patient_detail,
        name='patient-detail'),
    re_path(
        r'^patient/update/(?P<pk>[0-9]+)$',
        views.PatientUpdate.as_view(),
        name='patient-update'),
    re_path(
        r'^patient/activate_detail/(?P<pk>[0-9]+)$',
        views.patient_activate_detail,
        name='patient-activate-detail'),
    re_path(
        r'^patient/activate_home/(?P<pk>[0-9]+)$',
        views.patient_activate_home,
        name='patient-activate-home'),

    # PROVIDERS
    re_path(
        r'^new-provider/$',
        views.ProviderCreate.as_view(),
        name='new-provider'),
    re_path(
        r'^choose-role/$',
        views.choose_clintype,
        name='choose-clintype'),
    re_path(
        r'^provider-update/$',
        views.ProviderUpdate.as_view(),
        name='provider-update'),

    # ACTION ITEMS
    re_path(
        r'^(?P<pt_id>[0-9]+)/action-item/$',
        views.ActionItemCreate.as_view(),
        name='new-action-item'),
    re_path(
        r'^action-item/(?P<pk>[0-9]+)/update$',
        views.ActionItemUpdate.as_view(),
        name="update-action-item"),
    re_path(
        r'^action-item/(?P<ai_id>[0-9]+)/done$',
        views.done_action_item,
        name=models.ActionItem.MARK_DONE_URL_NAME),
    re_path(
        r'^action-item/(?P<ai_id>[0-9]+)/reset$',
        views.reset_action_item,
        name='reset-action-item'),

    # DOCUMENTS
    re_path(
        r'^(?P<pt_id>[0-9]+)/document/$',
        views.DocumentCreate.as_view(),
        name="new-document"),
    re_path(
        r'^document/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=models.Document),
        name="document-detail"),
    re_path(
        r'^document/update/(?P<pk>[0-9]+)$',
        views.DocumentUpdate.as_view(),
        name="document-update"),

    # MISC
    re_path(
        r'^about/',
        TemplateView.as_view(template_name='pttrack/about.html'),
        name='about'),
]


def wrap_url(url, no_wrap=[], login_only=[], provider_only=[],
             updated_provider_only=[]):
    '''
    Wrap URL in decorators as appropriate.
    '''
    if url.name in no_wrap:
        # do not wrap at all, fully public
        pass

    elif url.name in login_only:
        url.callback = login_required(url.callback)

    elif url.name in provider_only:
        url.callback = provider_required(url.callback)
        url.callback = login_required(url.callback)

    elif url.name in updated_provider_only:
        url.callback = provider_update_required(url.callback)
        url.callback = provider_required(url.callback)
        url.callback = login_required(url.callback)

    else:  # wrap in everything
        url.callback = clintype_required(url.callback)
        url.callback = provider_update_required(url.callback)
        url.callback = provider_required(url.callback)
        url.callback = login_required(url.callback)

    return url


wrap_config = {'no_wrap': ['about'],
               'login_only': ['new-provider'],
               'provider_only': ['provider-update'],
               'updated_provider_only': ['choose-clintype']}


urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlpatterns]
