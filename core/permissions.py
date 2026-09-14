from rest_framework import permissions
from django.utils import timezone
from datetime import timedelta

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user

class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

class IsParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.buyer == request.user or obj.seller == request.user

class CanEditWithinWindow(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.sender != request.user:
            return False
        timelapse = timezone.now() - obj.created_at
        return timelapse <= timedelta(minutes=30)

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

