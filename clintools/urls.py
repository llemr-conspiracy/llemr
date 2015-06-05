from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'clintools.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^pttrack/', include('pttrack.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
