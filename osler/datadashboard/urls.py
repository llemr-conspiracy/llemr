from __future__ import unicode_literals
from django.urls import re_path, path

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
    re_path(r'^send-json/', views.send_json, name='send_json'),
    re_path(r'^jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog')
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]
