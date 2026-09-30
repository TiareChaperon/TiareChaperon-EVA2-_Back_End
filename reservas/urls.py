from django.urls import path

from . import views


urlpatterns = [

    # ======================================================
    # VER CARRO
    # ======================================================

    path(
        "carro/",
        views.ver_carro,
        name="ver_carro",
    ),

    # ======================================================
    # AGREGAR AL CARRO
    # ======================================================

    path(
        "carro/agregar/",
        views.agregar_al_carro,
        name="agregar_al_carro",
    ),

    # ======================================================
    # ELIMINAR DEL CARRO
    # ======================================================

    path(
        "carro/eliminar/<int:item_id>/",
        views.eliminar_del_carro,
        name="eliminar_del_carro",
    ),
]
