from django.conf.urls import url
from pttrack.urls import url_wrap
from django.views.generic import DetailView

from . import models
from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    url(r'^new/(?P<pt_id>[0-9]+)/$',
        views.WorkupCreate.as_view(),
        name='new-workup'),
    url(r'^(?P<pk>[0-9]+)/$',
        DetailView.as_view(model=models.Workup),
        name='workup'),
    url(r'^(?P<pk>[0-9]+)/update/$',
        views.WorkupUpdate.as_view(),
        name='workup-update'),
    url(r'^(?P<pk>[0-9]+)/sign/$',
        views.sign_workup,
        name='workup-sign'),
    url(r'^(?P<pk>[0-9]+)/error/$',
        views.error_workup,
        name="workup-error"),

    url(r'^(?P<pt_id>[0-9]+)/clindate/$',
        views.ClinicDateCreate.as_view(),
        name="new-clindate"),
]

urlpatterns = url_wrap(unwrapped_urlconf)