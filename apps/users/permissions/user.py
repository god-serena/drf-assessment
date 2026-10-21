from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated

from ..models import Roles

class AdministratorPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            raise NotAuthenticated()
        
        has_permission = user.role == Roles.ADMIN.value
            
        return has_permission
            
        