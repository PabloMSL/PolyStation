from rest_framework import permissions

class IsVendedor(permissions.BasePermission):
    """
    Permitir el acceso unicamente a los usuarios con rol de Vendedor
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.rol == 'Vendedor')
    
class IsAdministrador(permissions.BasePermission):
    """
    Permitir el acceso unicamente a los usuarios con rol de Administrador 
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.rol == 'Administrador')