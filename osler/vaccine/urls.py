from __future__ import unicode_literals
from django.urls import path

from osler.core.urls import wrap_url
from . import views

unwrapped_urlconf = [
    path('<int:pt_id>/actionitem/<int:series_id>/',
         views.VaccineActionItemCreate.as_view(),
         name='new-vaccine-ai'),
    path('<int:pt_id>/followup/<int:ai_id>/',
         views.VaccineFollowupCreate.as_view(),
         name='new-vaccine-followup'),
    path('<int:pt_id>/select/',
         views.select_vaccine_series,
         name='select-vaccine-series'),
    path('<int:pt_id>/<int:series_id>/',
         views.VaccineDoseCreate.as_view(),
         name='new-vaccine-dose'),
    path('<int:pt_id>/',
         views.VaccineSeriesCreate.as_view(),
         name='new-vaccine-series'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]