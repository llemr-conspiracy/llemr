from __future__ import unicode_literals
from django.urls import re_path
from osler.core.urls import wrap_url
from osler.datadashboard import views

app_name = 'datadashboard'
unwrapped_urlconf = [
    re_path(r'^$', views.DataDashboardView.as_view(), name='patient-data-dashboard'),
    re_path(r'^hypertension-json/', views.send_hypertension_json, name='hypertension_json'),
    re_path(r'^diabetes-json/', views.send_diabetes_json, name='diabetes_json'),
    re_path(r'^all-json/', views.send_all_json, name='all_json'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]


