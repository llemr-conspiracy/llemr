from django.conf.urls import url
from django.views.generic import ListView
from . import models as mymodels
from . import views

urlpatterns = [
    url(r'^$', ListView.as_view(model=mymodels.Patient,)),
    url(r'^intake/$', views.intake, name="intake"),
    url(r'^(?P<pt_id>[0-9]+)/$', views.patient, name='patient'),
    url(r'^(?P<pt_id>[0-9]+)/followup/$', views.followup, name='followup'),
    url(r'^(?P<pt_id>[0-9]+)/workup/$', views.workup, name='workup')
]
