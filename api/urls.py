from django.urls import include, path
from .views import PeriodViewSet
from rest_framework.routers import SimpleRouter
app_name = "api"

router = SimpleRouter()
router.register("period", PeriodViewSet)
urlpatterns = [
    path("", include(router.urls)),
]
