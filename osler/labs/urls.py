from __future__ import unicode_literals
from django.urls import re_path
from osler.core.urls import wrap_url
from django.views.generic import DetailView

from . import models
from . import views

app_name = 'labs'
urlpatterns = [
    re_path(r'^all_list/(?P<pt_id>[0-9]+)/$',
        views.LabListView.as_view(),
        name="all-labs"),
    re_path(r'^all/(?P<pt_id>[0-9]+)/$',
        views.view_all_as_table,
        name="all-labs-table"),
    re_path(r'^all/(?P<pt_id>[0-9]+)/(?P<month_range>[0-9]+)$',
        views.view_all_as_table,
        name="all-labs-table-filter"),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.LabDetailView.as_view(),
        name='lab-detail'),
    re_path(r'^new/(?P<pt_id>[0-9]+)/(?P<lab_type_id>[0-9]+)/$',
        views.MeasurementsCreate.as_view(),
        name='new-full-lab'), #create all measurements assoc w/ the lab obj
    re_path(r'^new/(?P<pt_id>[0-9]+)/$',
        views.LabCreate.as_view(),
        name='new-lab'), #create "parent" lab object
    re_path(r'^edit/(?P<pk>[0-9]+)/$',
        views.MeasurementsEdit.as_view(),
        name='lab-edit'),
]
