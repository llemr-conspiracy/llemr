from __future__ import unicode_literals

from django.contrib import admin

# from django.conf.urls import include
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('pttrack/', include('pttrack.urls')),
    path('accounts/', include('pttrack.auth_urls')),
    path('followup/', include('followup.urls')),
    path('workup/', include('workup.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('demographics/', include('demographics.urls')),
    path('appointment/', include('appointment.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('api.urls')),
    path('referral/', include('referral.urls')),
    path('',
         RedirectView.as_view(pattern_name="dashboard-dispatch",
                              permanent=False),
         name='root'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
