from django.urls import path

from . import views


urlpatterns = [

    # ======================================================
    # CHECKOUT WEB
    # ======================================================

    path(
        "checkout/",
        views.checkout_web,
        name="checkout_web",
    ),

    # ======================================================
    # MIS BOLETOS
    # ======================================================

    path(
        "mis-boletos/",
        views.mis_boletos,
        name="mis_boletos_web",
    ),

    # ======================================================
    # DETALLE DE COMPRA
    # ======================================================

    path(
        "compra/<int:venta_id>/",
        views.compra_exitosa,
        name="compra_exitosa",
    ),

    # ======================================================
    # VALIDAR BOLETO
    # ======================================================

    path(
        "validar-boleto/",
        views.validar_boleto,
        name="validar_boleto",
    ),
]
