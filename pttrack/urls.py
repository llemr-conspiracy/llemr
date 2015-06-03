from django.conf.urls import url
from django.views.generic import ListView, DetailView
from . import models as mymodels
from . import views

urlpatterns = [
    url(r'^$', ListView.as_view(model=mymodels.Patient,)),
    url(r'^intake/$', views.intake, name="intake"),
    url(r'^clindate/(?P<pt_id>[0-9]+)/$', views.clindate, name="clindate"),
    url(r'^(?P<pt_id>[0-9]+)/$', views.patient, name='patient'),
    url(r'^(?P<pt_id>[0-9]+)/followup/$', views.followup, name='followup'),
    url(r'^(?P<pt_id>[0-9]+)/workup/$', views.new_workup, name='new-workup'),
    url(r'^(?P<pt_id>[0-9]+)/action-item/$', views.new_action_item, name='new-action-item'),
    url(r'^workup/(?P<pk>[0-9]+)$', DetailView.as_view(model=mymodels.Workup), name='workup'),
    url(r'^$', DetailView.as_view(model=mymodels.Workup,)),
]
