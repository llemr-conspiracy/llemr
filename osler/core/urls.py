from django.urls import re_path
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

from osler.core import models
from osler.core import views
from osler.core.decorators import active_role_required, user_init_required


app_name = 'core'
unwrapped_urlpatterns = [
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

    # USER MANAGEMENT
    re_path(
        r'^choose-role/$',
        views.choose_role,
        name='choose-role'),
    re_path(
        r'^user-init/$',
        views.UserInit.as_view(),
        name='user-init'),

    # ACTION ITEMS
    re_path(
        r'^(?P<pt_id>[0-9]+)/action-item/$',
        views.ActionItemCreate.as_view(),
        name='new-action-item'),
    re_path(
        r'^action-item/(?P<pk>[0-9]+)/update$',
        views.ActionItemUpdate.as_view(),
        name="update-action-item"),
    # re_path(
    #     r'^action-item/(?P<ai_id>[0-9]+)/done$',
    #     views.done_action_item,
    #     name=models.ActionItem.MARK_DONE_URL_NAME),
    re_path(
        r'^action-item/(?P<ai_id>[0-9]+)/reset$',
        views.reset_action_item,
        name='reset-action-item'),
    re_path(
        r'^action-item/(?P<ai_id>[0-9]+)/done$',
        views.actionitem_detail,
        name='done-action-item'),

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
]


def wrap_url(url, no_wrap=[], login_only=[], user_init_only=[]):
    '''
    Wrap URL in decorators as appropriate.
    '''
    if url.name in no_wrap:
        # do not wrap at all, fully public
        pass

    elif url.name in login_only:
        url.callback = login_required(url.callback)

    elif url.name in user_init_only:
        url.callback = user_init_required(url.callback)
        url.callback = login_required(url.callback)

    else:  # wrap in everything
        url.callback = active_role_required(url.callback)
        url.callback = user_init_required(url.callback)
        url.callback = login_required(url.callback)

    return url


wrap_config = {
    'login_only': ['user-init'],
    'user_init_only': ['choose-role']
}


urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlpatterns]
