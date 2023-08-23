from typing import Any
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwner(permissions.BasePermission):
    """ checks if owner of the object is the authenticated user or not. """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsPurchaseOwner(permissions.BasePermission):
    """ purchase object does not have owner field. this permission checks if
    purchases related periods owner is authenticated user or not.
    """
    def has_object_permission(self, request, view, obj):
        return obj.period.owner == request.user


class IsAuthorizedUser(permissions.BasePermission):
    """ make sure users can only edit their own user objects. """
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        return obj == request.user
