from django.conf.urls import url
from pttrack.urls import wrap_url
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
    url(r'^(?P<pk>[0-9]+)/pdf/$',
        views.pdf_workup,
        name="workup-pdf"),

    url(r'^(?P<pt_id>[0-9]+)/clindate/$',
        views.ClinicDateCreate.as_view(),
        name="new-clindate"),
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]