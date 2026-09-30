from django.urls import path

from .api_views import (
    AsientosServicioView,
    BuscarServiciosView,
    ServicioAdminDetailView,
    ServicioAdminListCreateView,
)


urlpatterns = [
    # ======================================================
    # API PÚBLICA - BÚSQUEDA DE SERVICIOS
    # ======================================================

    path(
        "servicios/buscar/",
        BuscarServiciosView.as_view(),
        name="buscar_servicios",
    ),

    # ======================================================
    # API PÚBLICA - ASIENTOS DE UN SERVICIO
    # ======================================================

    path(
        "servicios/<int:pk>/asientos/",
        AsientosServicioView.as_view(),
        name="asientos_servicio_api",
    ),

    # ======================================================
    # API ADMINISTRATIVA - LISTAR Y CREAR SERVICIOS
    # ======================================================

    path(
        "servicios/",
        ServicioAdminListCreateView.as_view(),
        name="servicios_admin",
    ),

    # ======================================================
    # API ADMINISTRATIVA - DETALLE, MODIFICAR Y ELIMINAR
    # ======================================================

    path(
        "servicios/<int:pk>/",
        ServicioAdminDetailView.as_view(),
        name="servicio_admin_detalle",
    ),
]
