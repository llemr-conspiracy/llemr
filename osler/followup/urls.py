from __future__ import unicode_literals
from django.urls import path
from osler.core.urls import wrap_url

from . import views

unwrapped_urlconf = [  # pylint: disable=invalid-name
    path('<int:pt_id>/actionitem/<int:ai_id>/',
         views.ActionItemFollowupCreate.as_view(),
         name='new-actionitem-followup'),
    path('<int:pt_id>/<str:ftype>/',
         views.FollowupCreate.as_view(),
         name='new-followup'),
    path('actionitemfu/<int:pk>/',
         views.ActionItemFollowupUpdate.as_view(),
         {"model": "Action Item"},
         name="followup"),
]

wrap_config = {}
urlpatterns = [wrap_url(u, **wrap_config) for u in unwrapped_urlconf]
