from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from platformUsers.pass_test import is_teacher


class TeacherPermission(permissions.BasePermission):
    message = "You're not allowed to perform this action"

    def has_permission(self, request, view):
        if request.method != "DELETE":
            return True
        else:
            if is_teacher(request.user):
                return True
            raise PermissionDenied
