from django.conf.urls import url

from pttrack.urls import url_wrap
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

# pylint: disable=I0011

unwrapped_urlpatterns = [  # pylint: disable=invalid-name
    url(r'^pt_list/$',
        views.PtList.as_view(),
        name='pt_list_api'),
]

urlpatterns = url_wrap(unwrapped_urlpatterns)
urlpatterns = format_suffix_patterns(urlpatterns)
