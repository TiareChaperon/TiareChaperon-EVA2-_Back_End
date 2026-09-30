from django.urls import path

from .api_views import (
    CambiarEstadoVentaView,
    CheckoutView,
    MisBoletosView,
)


urlpatterns = [
    # ==============================
    # CHECKOUT DE VENTA
    # ==============================

    path(
        "ventas/checkout/",
        CheckoutView.as_view(),
        name="venta_checkout",
    ),

    # ==============================
    # CAMBIAR ESTADO DE VENTA
    # ==============================

    path(
        "ventas/<int:pk>/estado/",
        CambiarEstadoVentaView.as_view(),
        name="cambiar_estado_venta",
    ),

    # ==============================
    # BOLETOS DEL PASAJERO
    # ==============================

    path(
        "mis-boletos/",
        MisBoletosView.as_view(),
        name="mis_boletos",
    ),
]
