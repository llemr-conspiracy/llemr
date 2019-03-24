from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^attending/$',
        views.attending_dashboard,
        name='attending-dashboard'),
]
