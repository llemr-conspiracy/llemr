from __future__ import unicode_literals
from django.urls import path
from django.views.generic import DetailView

from osler.core.urls import wrap_url

from osler.demographics import views
from osler.demographics import models


unwrapped_urlconf = [
    path('new/<int:pt_id>',
         views.DemographicsCreate.as_view(),
         name='demographics-create'),
    path('<int:pk>/',
         DetailView.as_view(model=models.Demographics),
         name='demographics-detail'),
    path('<int:pk>/update/',
         views.DemographicsUpdate.as_view(),
         name='demographics-update'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]
