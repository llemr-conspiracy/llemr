from django.conf.urls import url
from osler.core.urls import wrap_url
from django.views.generic import DetailView

from . import models
from . import views

unwrapped_urlconf = [
    url(r'^all_list/(?P<pt_id>[0-9]+)/$',
        views.LabListView.as_view(),
        name="all-labs"),
    url(r'^all/(?P<pt_id>[0-9]+)/$',
        views.view_all_as_table,
        name="all-labs-table"),
    #url(r'^all/(?P<pt_id>[0-9]+)/)$',
    #    views.view_all_as_table,
    #    name="all-labs-table-filter"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.LabDetailView.as_view(),
        name='lab-detail'),
    url(r'^new/(?P<pt_id>[0-9]+)/(?P<lab_type_id>[0-9]+)/$',
        views.full_lab_create,
        name='new-full-lab'), #create all measurements assoc w/ the lab obj
    url(r'^new/(?P<pt_id>[0-9]+)/$',
        views.lab_create,
        name='new-lab'), #create "parent" lab object
]

wrap_config = {}
urlpatterns = [wrap_url(url, **wrap_config) for url in unwrapped_urlconf]