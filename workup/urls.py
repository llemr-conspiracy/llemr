from django.conf.urls import url
from pttrack.urls import url_wrap
from django.views.generic import DetailView

from . import models
from . import views

#TODO: remove workup from the front of all these URLs
unwrapped_urlconf = [  # pylint: disable=invalid-name
    url(r'^(?P<pt_id>[0-9]+)/workup/$',
        views.WorkupCreate.as_view(),
        name='new-workup'),
    url(r'^workup/(?P<pk>[0-9]+)$',
        DetailView.as_view(model=models.Workup),
        name='workup'),
    url(r'^workup/update/(?P<pk>[0-9]+)$',
        views.WorkupUpdate.as_view(),
        name='workup-update'),
    url(r'^workup/sign/(?P<pk>[0-9]+)$',
        views.sign_workup,
        name='workup-sign'),
    url(r'^workup/error/(?P<pk>[0-9]+)$',
        views.error_workup,
        name="workup-error"),

    url(r'^clindate/(?P<pt_id>[0-9]+)/$',
        views.ClinicDateCreate.as_view(),
        name="new-clindate"),
]

urlpatterns = url_wrap(unwrapped_urlconf)