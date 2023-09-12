from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (PeriodShareViewSet, PeriodShareViewSetRetrieve,
                    PeriodViewSet, PersonViewSet, PurchaseViewSet)

app_name = "api"

router = SimpleRouter()
router.register("period", PeriodViewSet)
router.register("person", PersonViewSet)
router.register("purchase", PurchaseViewSet)
router.register("share/period", PeriodShareViewSet)
router.register("share", PeriodShareViewSetRetrieve)

urlpatterns = [
    path("", include(router.urls)),
]
