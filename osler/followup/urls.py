from __future__ import unicode_literals
from django.urls import path
from osler.core.urls import wrap_url

from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    path('<int:pt_id>/referral/',
         views.ReferralFollowupCreate.as_view(),
         name='new-referral-followup'),
    path('<int:pt_id>/<str:ftype>/',
         views.FollowupCreate.as_view(),
         name='new-followup'),
    path('<int:pt_id>/',
         views.followup_choice,
         name='followup-choice'),
    path('referral/<int:pk>/',
         views.ReferralFollowupUpdate.as_view(),
         {"model": "Referral"},
         name="followup"),  # parameter 'model' to identify from others w/ name
    path('lab/<int:pk>/',
         views.LabFollowupUpdate.as_view(),
         {"model": "Lab"},
         name="followup"),
    path('vaccine/<int:pk>/',
         views.VaccineFollowupUpdate.as_view(),
         {"model": "Vaccine"},
         name="followup"),
    path('general/<int:pk>/',
         views.GeneralFollowupUpdate.as_view(),
         {"model": "General"},
         name="followup"),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]
