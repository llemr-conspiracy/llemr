from __future__ import unicode_literals
from django.urls import path
from django.contrib.auth.views import LoginView

from . import forms


urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=forms.CrispyAuthenticationForm
    )),
]
