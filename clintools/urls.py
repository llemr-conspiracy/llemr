from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    # Examples:
    # url(r'^$', 'clintools.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^pttrack/', include('pttrack.urls')),
    url(r'^followup/', include('followup.urls')),
    url(r'^workup/', include('workup.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^$', RedirectView.as_view(pattern_name="home", permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
