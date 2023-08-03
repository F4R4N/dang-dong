from django.urls import include, path
from .views import PeriodViewSet, PersonViewSet, PurchaseViewSet, PurchaseExpenseDetail
from rest_framework.routers import SimpleRouter
app_name = "api"

router = SimpleRouter()
router.register("period", PeriodViewSet)
router.register("person", PersonViewSet)
router.register("purchase", PurchaseViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("purchase/detail/<slug:pk>", PurchaseExpenseDetail.as_view())
    
]
