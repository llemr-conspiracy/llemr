from django.urls import path

from . import views

app_name = 'surveys'
urlpatterns = [
    path('test/', views.test, name='test'),
    path('', views.SurveyTemplateListView.as_view(), name='surveys')
]
