from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from osler.users.api.views import UserViewSet
from osler.inventory.api.views import InventoryViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("inventory", InventoryViewSet)


app_name = "api"
urlpatterns = router.urls
