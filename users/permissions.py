from rest_framework import permissions

from PerfectTaxi.exceptions import BaseAPIException
from users.models import User


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_admin()


class IsDeveloper(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_developer()


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_customer()


class IsNotBlocked(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.blocked_at == None


class IsConfirmed(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.confirmed_at != None


class CanResetPassword(permissions.BasePermission):
    def has_permission(self, request, view):
        exists_user = User.objects.filter(
            email=request.data.get('email'),
            confirmed_at__isnull=False,
            blocked_at__isnull=True,
        ).exists()

        if not exists_user:
            raise BaseAPIException('Пользователь не найден')
        return True


class CanHandleRequest(permissions.BasePermission):
    def has_permission(self, request, view):
        user: User = request.user
        if not bool(user and user.is_authenticated):
            return False
        if not user.is_admin():
            return False
        if not user.confirmed_at or user.blocked_at:
            return False
        return True


class IsActive(permissions.BasePermission):
    def has_permission(self, request, view):
        user: User = request.user
        if not bool(user and user.is_authenticated):
            return False
        if not user.confirmed_at or user.is_block:
            return False
        return True

class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        user: User = request.user
        if user:
            if user.role == 'driver':
                return True
        return False

class CanChangeStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        user: User = request.user
        if user:
            if user.role == 'driver' or user.role == "admin":
                return True
        return False

class CanHandleAdmin(CanHandleRequest):
    pass