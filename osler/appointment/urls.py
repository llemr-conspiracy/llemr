from __future__ import unicode_literals
from django.urls import path
from osler.core.urls import wrap_url

from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    path(r'new',
         views.AppointmentCreate.as_view(),
         name='appointment-new'),
    path(r'<int:pk>/update',
         views.AppointmentUpdate.as_view(),
         name='appointment-update'),
    path(r'list',
         views.list_view,
         name='appointment-list'),
    path(r'<int:pk>/noshow',
         views.mark_no_show,
         name='appointment-mark-no-show'),
    path(r'<int:pk>/arrived',
         views.mark_arrived,
         name='appointment-mark-arrived'),
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]
