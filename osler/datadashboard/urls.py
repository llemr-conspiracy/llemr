from __future__ import unicode_literals
from django.urls import re_path

from osler.core.urls import wrap_url
from osler.datadashboard import views

app_name = 'datadashboard'
unwrapped_urlconf = [
    re_path(
        r'^$',
        views.display_hypertensive,
        name='display-hypertensive'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]
