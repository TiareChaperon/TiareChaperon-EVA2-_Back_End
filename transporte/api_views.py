from rest_framework import generics
from rest_framework.permissions import AllowAny

from accounts.permissions import IsAdministradorFlota

from .filters import ServicioFilter
from .models import AsientoServicio, Servicio
from .serializers import (
    AsientoServicioSerializer,
    ServicioAdminSerializer,
    ServicioSerializer,
)


# ==========================================================
# BÚSQUEDA PÚBLICA DE SERVICIOS
# ==========================================================

class BuscarServiciosView(generics.ListAPIView):
    """
    Permite buscar servicios activos.

    Esta API es pública y puede filtrarse por:
    - Ciudad de origen.
    - Ciudad de destino.
    - Fecha de salida.
    """

    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]
    filterset_class = ServicioFilter

    queryset = (
        Servicio.objects
        .filter(
            activo=True
        )
        .select_related(
            "ruta",
            "ruta__terminal_origen",
            "ruta__terminal_origen__ciudad",
            "ruta__terminal_destino",
            "ruta__terminal_destino__ciudad",
            "bus",
        )
        .prefetch_related(
            "asientos_servicio"
        )
        .order_by(
            "fecha_hora_salida"
        )
    )


# ==========================================================
# ASIENTOS DE UN SERVICIO
# ==========================================================

class AsientosServicioView(generics.ListAPIView):
    """
    Muestra los asientos correspondientes
    a un servicio específico.

    Esta API es pública.
    """

    serializer_class = AsientoServicioSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Obtiene los asientos pertenecientes
        al servicio indicado en la URL.
        """

        servicio_id = self.kwargs["pk"]

        return (
            AsientoServicio.objects
            .filter(
                servicio_id=servicio_id
            )
            .select_related(
                "asiento",
                "servicio",
                "servicio__bus",
            )
            .order_by(
                "asiento__numero"
            )
        )


# ==========================================================
# API ADMINISTRATIVA DE SERVICIOS
# ==========================================================

class ServicioAdminListCreateView(
    generics.ListCreateAPIView
):
    """
    Permite al Administrador de Flota
    listar y crear servicios.
    """

    serializer_class = ServicioAdminSerializer
    permission_classes = [IsAdministradorFlota]

    queryset = (
        Servicio.objects
        .select_related(
            "ruta",
            "ruta__terminal_origen",
            "ruta__terminal_origen__ciudad",
            "ruta__terminal_destino",
            "ruta__terminal_destino__ciudad",
            "bus",
        )
        .order_by(
            "fecha_hora_salida"
        )
    )


# ==========================================================
# DETALLE ADMINISTRATIVO DE SERVICIO
# ==========================================================

class ServicioAdminDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Permite al Administrador de Flota
    consultar, modificar o eliminar
    un servicio específico.
    """

    serializer_class = ServicioAdminSerializer
    permission_classes = [IsAdministradorFlota]

    queryset = (
        Servicio.objects
        .select_related(
            "ruta",
            "ruta__terminal_origen",
            "ruta__terminal_origen__ciudad",
            "ruta__terminal_destino",
            "ruta__terminal_destino__ciudad",
            "bus",
        )
        .all()
    )
