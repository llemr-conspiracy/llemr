from __future__ import unicode_literals
from django.conf.urls import url

from pttrack.urls import wrap_url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

# pylint: disable=I0011

unwrapped_urlpatterns = [  # pylint: disable=invalid-name
    url(r'pt_list/', views.PtList.as_view(), name='pt_list_api'),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlpatterns]
urlpatterns = format_suffix_patterns(urlpatterns)
