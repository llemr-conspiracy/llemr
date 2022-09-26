from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView, RedirectView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', RedirectView.as_view(pattern_name="dashboard-dispatch", permanent=False),
         name="home"),

    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("osler.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),

    # Osler apps here:
    path('core/', include('osler.core.urls')),
    path('followup/', include('osler.followup.urls')),
    path('workup/', include('osler.workup.urls')),
    path('dashboard/', include('osler.dashboard.urls')),
    path('demographics/', include('osler.demographics.urls')),
    path('appointment/', include('osler.appointment.urls')),
    path('referral/', include('osler.referral.urls')),
    path('vaccine/', include('osler.vaccine.urls')),
    path('labs/', include('osler.labs.urls')),
    path('inventory/', include('osler.inventory.urls')),
    path('surveys/', include('osler.surveys.urls')),
    #path('datadashboard/', include('osler.datadashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
