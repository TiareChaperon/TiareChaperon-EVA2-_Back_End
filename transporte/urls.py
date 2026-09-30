from django.urls import path

from . import views


urlpatterns = [

    # ======================================================
    # PASAJEROS
    # ======================================================

    path(
        "buscar-pasajes/",
        views.buscar_pasajes,
        name="buscar_pasajes",
    ),

    path(
        "servicio/<int:servicio_id>/asientos/",
        views.seleccionar_asientos,
        name="seleccionar_asientos",
    ),


    # ======================================================
    # CIUDADES
    # ======================================================

    path(
        "ciudades/",
        views.ciudad_lista,
        name="ciudad_lista",
    ),

    path(
        "ciudades/crear/",
        views.ciudad_crear,
        name="ciudad_crear",
    ),

    path(
        "ciudades/<int:pk>/editar/",
        views.ciudad_editar,
        name="ciudad_editar",
    ),

    path(
        "ciudades/<int:pk>/eliminar/",
        views.ciudad_eliminar,
        name="ciudad_eliminar",
    ),


    # ======================================================
    # TERMINALES
    # ======================================================

    path(
        "terminales/",
        views.terminal_lista,
        name="terminal_lista",
    ),

    path(
        "terminales/crear/",
        views.terminal_crear,
        name="terminal_crear",
    ),

    path(
        "terminales/<int:pk>/editar/",
        views.terminal_editar,
        name="terminal_editar",
    ),

    path(
        "terminales/<int:pk>/eliminar/",
        views.terminal_eliminar,
        name="terminal_eliminar",
    ),


    # ======================================================
    # RUTAS
    # ======================================================

    path(
        "rutas/",
        views.ruta_lista,
        name="ruta_lista",
    ),

    path(
        "rutas/crear/",
        views.ruta_crear,
        name="ruta_crear",
    ),

    path(
        "rutas/<int:pk>/editar/",
        views.ruta_editar,
        name="ruta_editar",
    ),

    path(
        "rutas/<int:pk>/eliminar/",
        views.ruta_eliminar,
        name="ruta_eliminar",
    ),


    # ======================================================
    # BUSES
    # ======================================================

    path(
        "buses/",
        views.bus_lista,
        name="bus_lista",
    ),

    path(
        "buses/crear/",
        views.bus_crear,
        name="bus_crear",
    ),

    path(
        "buses/<int:pk>/editar/",
        views.bus_editar,
        name="bus_editar",
    ),

    path(
        "buses/<int:pk>/eliminar/",
        views.bus_eliminar,
        name="bus_eliminar",
    ),


    # ======================================================
    # ASIENTOS
    # ======================================================

    path(
        "asientos/",
        views.asiento_lista,
        name="asiento_lista",
    ),

    path(
        "asientos/crear/",
        views.asiento_crear,
        name="asiento_crear",
    ),

    path(
        "asientos/<int:pk>/editar/",
        views.asiento_editar,
        name="asiento_editar",
    ),

    path(
        "asientos/<int:pk>/eliminar/",
        views.asiento_eliminar,
        name="asiento_eliminar",
    ),


    # ======================================================
    # SERVICIOS
    # ======================================================

    path(
        "servicios/",
        views.servicio_lista,
        name="servicio_lista",
    ),

    path(
        "servicios/crear/",
        views.servicio_crear,
        name="servicio_crear",
    ),

    path(
        "servicios/<int:pk>/editar/",
        views.servicio_editar,
        name="servicio_editar",
    ),

    path(
        "servicios/<int:pk>/eliminar/",
        views.servicio_eliminar,
        name="servicio_eliminar",
    ),


    # ======================================================
    # ASIENTOS POR SERVICIO
    # ======================================================

    path(
        "asientos-servicio/",
        views.asiento_servicio_lista,
        name="asiento_servicio_lista",
    ),

    path(
        "asientos-servicio/crear/",
        views.asiento_servicio_crear,
        name="asiento_servicio_crear",
    ),

    path(
        "asientos-servicio/<int:pk>/editar/",
        views.asiento_servicio_editar,
        name="asiento_servicio_editar",
    ),

    path(
        "asientos-servicio/<int:pk>/eliminar/",
        views.asiento_servicio_eliminar,
        name="asiento_servicio_eliminar",
    ),
]
