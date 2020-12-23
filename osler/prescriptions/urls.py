from functools import partial

from django.urls import re_path
from django.views.generic import DetailView

from osler.core.urls import wrap_url
from osler.prescriptions import models, views

unwrapped_urlconf = [

    re_path(
        r'^(?P<pk>[0-9]+)/new-prescription/$',
        views.PrescriptionCreate.as_view(),
        name='new-prescription')
]


wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]
