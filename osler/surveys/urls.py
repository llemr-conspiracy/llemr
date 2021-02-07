from django.urls import path, re_path
from osler.core.decorators import active_role_required, user_init_required
from django.contrib.auth.decorators import login_required
from osler.core.urls import wrap_url

from . import views

app_name = 'surveys'
unwrapped_urlpatterns = [
    path('test/', views.test, name='test'),
    path('', views.SurveyTemplateListView.as_view(), name='surveys'),
    re_path(r'^(?P<id>[0-9]+)/edit/?$', views.SurveyTemplateListView.as_view(), name='edit'),
    path('create/', views.create, name='create'),

]

# see core/urls.py if you want to remove login restrictions for certian views
urlpatterns = [wrap_url(u) for u in unwrapped_urlpatterns]
