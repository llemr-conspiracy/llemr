from __future__ import unicode_literals
from django.conf.urls import url
from osler.core.urls import wrap_url
from django.views.generic import DetailView

from . import models
from . import views

app_name = 'labs'
unwrapped_urlconf = [
    url(r'^all_list/(?P<pt_id>[0-9]+)/$',
        views.LabListView.as_view(),
        name="all-labs"),
    url(r'^all/(?P<pt_id>[0-9]+)/$',
        views.view_all_as_table,
        name="all-labs-table"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.LabDetailView.as_view(),
        name='lab-detail'),
    url(r'^new/(?P<pt_id>[0-9]+)/(?P<lab_type_id>[0-9]+)/$',
        views.full_lab_create,
        name='new-full-lab'), #create all measurements assoc w/ the lab obj
    url(r'^new/(?P<pt_id>[0-9]+)/$',
        views.lab_create,
        name='new-lab'), #create "parent" lab object
    url(r'^delete/(?P<pk>[0-9]+)/$',
        views.lab_delete,
        name='lab-delete'),
    url(r'^edit/(?P<pk>[0-9]+)/$',
        views.lab_edit,
        name='lab-edit'),
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]