from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib.auth.views import login

from . import forms


urlpatterns = [
    url(r'^login/$', login, {
        'template_name': 'registration/login.html',
        'authentication_form': forms.CrispyAuthenticationForm
        }),
    ]
