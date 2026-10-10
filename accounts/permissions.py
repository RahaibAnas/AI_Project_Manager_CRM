from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.role == "ADMIN":
            return True 


#admin
# admin@crm.com 12345
