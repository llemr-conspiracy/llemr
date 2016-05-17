from django.conf.urls import url
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView

from django.contrib.auth.decorators import login_required

from pttrack.decorators import provider_required
# from . import models as mymodels
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

# pylint: disable=I0011

unwrapped_urlpatterns = [  # pylint: disable=invalid-name
    url(r'^pt_list/$',
        views.PtList.as_view(),
        name='pt_list_api'),
]

def url_wrap(urls):
    '''
    Wrap URLs in login_required and provider_required decorators as
    appropriate.
    '''
    wrapped_urls = []
    for u in urls:
        if u.name in ['new-provider', 'choose-clintype']:
            # do not wrap in full regalia
            u._callback = login_required(u._callback)
        elif u.name in ['about']:
            # do not wrap at all, fully public
            pass
        else:
            u._callback = provider_required(u._callback)

        wrapped_urls.append(u)
    return wrapped_urls

urlpatterns = url_wrap(unwrapped_urlpatterns)
urlpatterns = format_suffix_patterns(urlpatterns)
