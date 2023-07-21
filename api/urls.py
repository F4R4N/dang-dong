from django.urls import include, path
from .views import PeriodViewSet, PersonViewSet
from rest_framework.routers import SimpleRouter
app_name = "api"

router = SimpleRouter()
router.register("period", PeriodViewSet)
router.register("person", PersonViewSet)
urlpatterns = [
    path("", include(router.urls)),
    
]
