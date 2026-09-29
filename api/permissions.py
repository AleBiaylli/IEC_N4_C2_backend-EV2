from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: permite lectura (GET) a cualquier usuario,
    pero requiere ser administrador/staff para modificar datos (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        # MÉTODOS DE LECTURA (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # MÉTODOS DE ESCRITURA
        return bool(request.user and request.user.is_staff)