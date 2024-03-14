from rest_framework import permissions

class VerDashboardPermission(permissions.BasePermission):
    """
    Permite el acceso al dashboard solo a usuarios con ciertos permisos.
    """
    
    def has_permission(self, request, view):
        # Aquí puedes implementar la lógica para verificar si el usuario tiene el permiso necesario.
        # Por ejemplo:
        return request.user.has_perm('evaluaciones.imagenes')