from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^pttrack/', include('pttrack.urls')),
    url(r'^accounts/', include('pttrack.auth_urls')),
    url(r'^followup/', include('followup.urls')),
    url(r'^workup/', include('workup.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^demographics/', include('demographics.urls')),
    url(r'^appointment/', include('appointment.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^referral/', include('referral.urls')),
    url(r'^accounts/', include('django_registration.backends.one_step.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$',
        RedirectView.as_view(pattern_name="dashboard-dispatch",
                             permanent=False),
        name='root'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
