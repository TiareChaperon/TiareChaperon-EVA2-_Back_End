from django.urls import path

from . import views


# ==============================
# RUTAS DE USUARIOS
# ==============================

urlpatterns = [

    path(
        "",
        views.inicio,
        name="inicio",
    ),

    path(
        "registro/",
        views.registro_pasajero,
        name="registro",
    ),

    path(
        "login/",
        views.iniciar_sesion,
        name="login",
    ),

    path(
        "logout/",
        views.cerrar_sesion,
        name="logout",
    ),

]
