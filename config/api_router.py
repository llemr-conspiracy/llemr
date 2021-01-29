from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from osler.users.api.views import UserViewSet
from osler.core.api.views import PatientViewSet
from osler.appointment.api.views import AppointmentViewSet
from osler.demographics.api.views import DemographicsViewSet
from osler.referral.api.views import ReferralViewSet
from osler.labs.api.views import LabViewSet
from osler.inventory.api.views import DrugViewSet
from osler.workup.api.views import WorkupViewSet
from osler.core.api.views import PatientViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("patients", PatientViewSet)
router.register("workups",WorkupViewSet)
router.register("appointments", AppointmentViewSet)
router.register("demographics", DemographicsViewSet)
router.register("referrals", ReferralViewSet)
router.register("labs", LabViewSet)
router.register("drugs", DrugViewSet)

app_name = "api"
urlpatterns = router.urls
