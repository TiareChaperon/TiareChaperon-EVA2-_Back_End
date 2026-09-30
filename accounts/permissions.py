from rest_framework.permissions import BasePermission


# ==============================
# PERMISO PASAJERO
# ==============================

class IsPasajero(BasePermission):
    """
    Permite el acceso únicamente a usuarios autenticados
    cuyo rol sea PASAJERO.

    Se utilizará principalmente para proteger el carro
    de pasajes, checkout y consulta de boletos.
    """

    message = "Debes ser un pasajero para realizar esta acción."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "PASAJERO"
        )


# ==============================
# PERMISO ADMINISTRADOR DE FLOTA
# ==============================

class IsAdministradorFlota(BasePermission):
    """
    Permite el acceso únicamente a usuarios autenticados
    cuyo rol sea ADMIN_FLOTA.

    Se utilizará para la administración de servicios,
    inventario y cambios de estado de las ventas.
    """

    message = (
        "Debes ser Administrador de Flota "
        "para realizar esta acción."
    )

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN_FLOTA"
        )
