from django.conf.urls import url
from pttrack.urls import wrap_url

from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    url(r'^new$',
        views.AppointmentCreate.as_view(),
        name='appointment-new'),
    url(r'^(?P<pk>[0-9]+)/update$',
        views.AppointmentUpdate.as_view(),
        name='appointment-update'),
    url(r'^list$',
        views.list_view,
        name='appointment-list'),
    url(r'^(?P<pk>[0-9]+)/noshow$',
        views.mark_no_show,
        name='appointment-mark-no-show'),
    url(r'^(?P<pk>[0-9]+)/arrived$',
        views.mark_arrived,
        name='appointment-mark-arrived'),
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]
