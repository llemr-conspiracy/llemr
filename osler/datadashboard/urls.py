from __future__ import unicode_literals
from django.urls import re_path
from django.views.i18n import JavaScriptCatalog
from osler.core.urls import wrap_url
from osler.datadashboard import views

js_info_dict = {
    'packages': ('datadashboard',),
}

app_name = 'datadashboard'
unwrapped_urlconf = [
    re_path(r'^$', views.DataDashboardView.as_view(), name='clinic-data-dashboard'),
    re_path(r'^patientdata-json-datadashboard/', views.send_patientdata_json, name='patientdata-json-datadashboard'),
    re_path(r'^context-json-datadashboard/', views.send_context_json, name='context-json-datadashboard'),
    re_path(r'^jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]


