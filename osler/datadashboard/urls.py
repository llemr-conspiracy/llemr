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
    re_path(r'^$', views.DataDashboardView.as_view(), name='patient-data-dashboard'),
    re_path(r'^all-json-datadashboard/', views.send_all_json, name='all_json_datadashboard'),
    re_path(r'^jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^export-csv/', views.export_csv, name='export-csv'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]


