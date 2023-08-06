from django.urls import path, include
from .views import LogoutView, MagicLinkView, UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import routers
app_name = "customauth"

router = routers.SimpleRouter()
router.register("user", UserViewSet)

urlpatterns = [
    path('login/magic/', MagicLinkView.as_view(), name='auth_magic_login'),
    path('login/magic/<code>/', MagicLinkView.as_view(), name="auth_magic_code"),
    path('login/refresh/', TokenRefreshView.as_view(), name='auth_refresh_token'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path("", include(router.urls)),
]
