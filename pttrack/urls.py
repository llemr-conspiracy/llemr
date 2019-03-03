from django.conf.urls import url
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

from django.contrib.auth.decorators import login_required
from .decorators import provider_required, clintype_required, \
    provider_update_required
from . import models
from . import views

# pylint: disable=I0011

unwrapped_urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$',
        views.home_page,
        name="home"),
    url(r'^all/$',
        views.all_patients,
        name="all-patients"),
    url(r'^preintake-select/$',
        views.PreIntakeSelect.as_view(),
        name="preintake-select"),
    url(r'^preintake/$',
        views.PreIntake.as_view(),
        name="preintake"),
    url(r'^intake/$',
        views.PatientCreate.as_view(),
        name="intake"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.patient_detail,
        name='patient-detail'),
    url(r'^patient/update/(?P<pk>[0-9]+)$',
        views.PatientUpdate.as_view(),
        name='patient-update'),
    url(r'^patient/activate_detail/(?P<pk>[0-9]+)$',
        views.patient_activate_detail,
        name='patient-activate-detail'),
    url(r'^patient/activate_home/(?P<pk>[0-9]+)$',
        views.patient_activate_home,
        name='patient-activate-home'),

    # PROVIDERS
    url(r'^new-provider/$',
        views.ProviderCreate.as_view(),
        name='new-provider'),
    url(r'^choose-role/$',
        views.choose_clintype,
        name='choose-clintype'),
    url(r'^provider-update/$',
        views.ProviderUpdate.as_view(),
        name='provider-update'),

    # ACTION ITEMS
    url(r'^(?P<pt_id>[0-9]+)/action-item/$',
        views.ActionItemCreate.as_view(),
        name='new-action-item'),
    url(r'^action-item/(?P<pk>[0-9]+)/update$',
        views.ActionItemUpdate.as_view(),
        name="update-action-item"),
    url(r'^action-item/(?P<ai_id>[0-9]+)/done$',
        views.done_action_item,
        name='done-action-item'),
    url(r'^action-item/(?P<ai_id>[0-9]+)/reset$',
        views.reset_action_item,
        name='reset-action-item'),

    # DOCUMENTS
    url(r'^(?P<pt_id>[0-9]+)/document/$',
        views.DocumentCreate.as_view(),
        name="new-document"),
    url(r'^document/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=models.Document),
        name="document-detail"),
    url(r'^document/update/(?P<pk>[0-9]+)$',
        views.DocumentUpdate.as_view(),
        name="document-update"),

    # MISC
    url(r'^about/',
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
