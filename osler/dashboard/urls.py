from __future__ import unicode_literals
from django.urls import path

from pttrack.urls import wrap_url
from . import views

unwrapped_urlconf = [
    path(r'dispatch/',
         views.dashboard_dispatch,
         name='dashboard-dispatch'),
    path(r'attending/',
         views.dashboard_attending,
         name='dashboard-attending'),
]

urlpatterns = [wrap_url(u, **{}) for u in unwrapped_urlconf]
