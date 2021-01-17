from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from osler.users.api.views import UserViewSet
from osler.core.api.views import PatientViewSet
from osler.appointment.api.views import AppointmentViewSet
from osler.demographics.api.views import DemographicsViewSet
from osler.referral.api.views import ReferralViewSet
from osler.labs.api.views import LabViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("user", UserViewSet)
router.register("patient", PatientViewSet)
router.register("appointment", AppointmentViewSet)
router.register("demographics", DemographicsViewSet)
router.register("referral", ReferralViewSet)
router.register("labs", LabViewSet)

app_name = "api"
urlpatterns = router.urls
