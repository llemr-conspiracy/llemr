from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from osler.users.api.views import UserViewSet
from osler.surveys.api.views import SurveyViewSet, QuestionViewSet, ChoiceViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("surveys", SurveyViewSet)
router.register("questions", QuestionViewSet)
router.register("choices", ChoiceViewSet)

app_name = "api"
urlpatterns = router.urls

