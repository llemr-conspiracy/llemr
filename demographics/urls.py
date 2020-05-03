from __future__ import unicode_literals
from django.urls import path
from pttrack.urls import wrap_url
from django.views.generic import DetailView

from . import views
from . import models as mymodels

unwrapped_urlconf = [  # pylint: disable=invalid-name
    path('new/<int:pt_id>',
         views.DemographicsCreate.as_view(),
         name='demographics-create'),
    path('<int:pk>/',
         DetailView.as_view(model=mymodels.Demographics),
         name='demographics-detail'),
    path('<int:pk>/update/',
         views.DemographicsUpdate.as_view(),
         name='demographics-update'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]
