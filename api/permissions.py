from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """ checks if owner of the object is the authenticated user or not."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsPurchaseOwner(permissions.BasePermission):
    """ purchase object does not have owner field. this permission checks if
    purchases related periods owner is authenticated user or not.
    """
    def has_object_permission(self, request, view, obj):
        print(obj.period.owner == request.user)
        return obj.period.owner == request.user
