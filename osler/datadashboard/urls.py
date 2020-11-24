from __future__ import unicode_literals
from django.urls import re_path
from django.views.i18n import JavaScriptCatalog
from osler.core.urls import wrap_url
from osler.datadashboard import views


# from django.urls import include, path
# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'workups', views.WorkupViewSet, basename='user')
# urlpatterns = router.urls

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
# # urlpatterns = [
# #     path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# # ]

js_info_dict = {
    'packages': ('datadashboard',),
}

app_name = 'datadashboard'
unwrapped_urlconf = [
    re_path(r'^$', views.DataDashboardView.as_view(), name='patient-data-dashboard'),
    # re_path(r'^hypertension-json/', views.send_hypertension_json, name='hypertension_json'),
    # re_path(r'^diabetes-json/', views.send_diabetes_json, name='diabetes_json'),
    re_path(r'^all-json/', views.send_all_json, name='all_json'),
    re_path(r'^jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^export-csv/', views.export_csv, name='export-csv'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]


