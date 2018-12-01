import os
import logging

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from django.conf import settings

from sendfile import sendfile

logger = logging.getLogger(__name__)


@login_required
def send_media_file(request, filename):
    fq_filename = os.path.join(settings.SENDFILE_ROOT, filename)
    logger.debug("Serving file %s with sendfile.", fq_filename)
    return sendfile(request, fq_filename)


urlpatterns = [
    url(r'^pttrack/', include('pttrack.urls')),
    url(r'^accounts/', include('pttrack.auth_urls')),
    url(r'^followup/', include('followup.urls')),
    url(r'^workup/', include('workup.urls')),
    url(r'^demographics/', include('demographics.urls')),
    url(r'^appointment/', include('appointment.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^media_auth/(?P<filename>.*)$', send_media_file),
    url(r'^referral/', include('referral.urls')),
    url(r'^$', RedirectView.as_view(pattern_name="home", permanent=False)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
