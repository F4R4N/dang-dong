from typing import Any
from rest_framework import permissions, status, mixins
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import (UserSerializer, MagicLinkSerializer,)
from .models import Verification
from .utils import auth_email
import secrets
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from api.permissions import IsAuthorizedUser
from api.responses import RESPONSE_MESSAGES
from django.contrib.auth import get_user_model


class LogoutView(APIView):
    """ send the refresh token as refresh_token in data """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                status=status.HTTP_205_RESET_CONTENT,
                data={'detail': "logged out"})

        except Exception:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "refresh_token is not valid"})


class MagicLinkView(APIView):
    """ register or log in the user with magic link """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = MagicLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        email = request.data["email"]
        try:
            user = get_user_model().objects.get(email=email)
            status_, data_ = auth_email(user)
            return Response(status=status_, data=data_)
        except get_user_model().DoesNotExist:
            user = get_user_model().objects.create(
                email=email,
                username=secrets.token_urlsafe(16),
                is_active=True,
            )
            status_, data_ = auth_email(user)
            return Response(status=status.HTTP_201_CREATED, data=data_)

    def get(self, request, code=None, format=None):
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": "required url argument 'code' is missing"})
        magic_link = get_object_or_404(Verification, code=code)
        if magic_link.is_expired():
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"detail": "The Token is expired, ask for another one"})
        refresh = RefreshToken.for_user(magic_link.user)
        serializer = UserSerializer(magic_link.user)
        magic_link.user.is_verified = True
        magic_link.user.save()

        data = {
            "user": serializer.data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            },
        }
        return Response(status=status.HTTP_200_OK, data=data)


class UserViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (permissions.IsAuthenticated, IsAuthorizedUser)
    serializer_class = UserSerializer
    http_method_names = ["get", "put", "delete"]

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        return Response(status=status.HTTP_204_NO_CONTENT, data=RESPONSE_MESSAGES["successfully_deleted"])

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        serializer = self.get_serializer(user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
