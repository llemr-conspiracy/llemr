from django.urls import path, re_path
from osler.core.urls import wrap_url

from . import views

app_name = 'surveys'
unwrapped_urlpatterns = [
    path('', views.SurveyListView.as_view(), name='surveys'),
    path('create/', views.create, name='create'),
    path('incomplete/<int:pid>', views.incomplete, name="incomplete"),
    re_path(r'^(?P<id>[0-9]+)/?$', views.view, name='view'),
    re_path(r'^(?P<id>[0-9]+)/edit/?$', views.SurveyListView.as_view(), name='edit'),
    re_path(r'^(?P<pid>[0-9]+)/fill/(?P<id>[0-9]+)/?$', views.fill, name='fill'),
    re_path(r'^(?P<pid>[0-9]+)/submit/(?P<id>[0-9]+)/?$', views.submit, name='submit'),
    re_path(r'^(?P<id>[0-9]+)/responses/?$', views.ResponsesListView.as_view(), name='responses'),
    path('responses/', views.AllResponsesListView.as_view(), name='all_responses'),
    re_path(r'^responses/(?P<id>[0-9]+)/?$', views.response, name='response'),
]

wrap_config = {
    # 'user_init_only': ['create', 'surveys', 'edit', 'fill']
}

# see core/urls.py if you want to remove login restrictions for certian views
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlpatterns]
