from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AsientoForm,
    AsientoServicioForm,
    BusForm,
    CiudadForm,
    RutaForm,
    ServicioForm,
    TerminalForm,
)

from .models import (
    Asiento,
    AsientoServicio,
    Bus,
    Ciudad,
    Ruta,
    Servicio,
    Terminal,
)


# ==========================================================
# CONTROL DE ACCESO ADMIN FLOTA
# ==========================================================

def admin_flota_required(view_func):
    """
    Restringe las vistas HTML para que solamente puedan
    ser utilizadas por usuarios con rol ADMIN_FLOTA.
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if request.user.role != "ADMIN_FLOTA":
            messages.error(
                request,
                "No tienes permisos para acceder a esta sección."
            )

            return redirect("inicio")

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================================
# CRUD DE CIUDADES
# ==========================================================


# ==============================
# LISTAR CIUDADES
# ==============================

@admin_flota_required
def ciudad_lista(request):
    """
    Muestra todas las ciudades registradas.
    """

    ciudades = Ciudad.objects.all().order_by("nombre")

    return render(
        request,
        "transporte/ciudades/lista.html",
        {
            "ciudades": ciudades,
        },
    )


# ==============================
# CREAR CIUDAD
# ==============================

@admin_flota_required
def ciudad_crear(request):
    """
    Permite registrar una nueva ciudad.
    """

    if request.method == "POST":
        form = CiudadForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Ciudad registrada correctamente."
            )

            return redirect("ciudad_lista")

    else:
        form = CiudadForm()

    return render(
        request,
        "transporte/ciudades/formulario.html",
        {
            "form": form,
            "titulo": "Registrar ciudad",
        },
    )


# ==============================
# EDITAR CIUDAD
# ==============================

@admin_flota_required
def ciudad_editar(request, pk):
    """
    Permite modificar una ciudad existente.
    """

    ciudad = get_object_or_404(
        Ciudad,
        pk=pk,
    )

    if request.method == "POST":
        form = CiudadForm(
            request.POST,
            instance=ciudad,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Ciudad actualizada correctamente."
            )

            return redirect("ciudad_lista")

    else:
        form = CiudadForm(
            instance=ciudad,
        )

    return render(
        request,
        "transporte/ciudades/formulario.html",
        {
            "form": form,
            "titulo": "Editar ciudad",
            "ciudad": ciudad,
        },
    )


# ==============================
# ELIMINAR CIUDAD
# ==============================

@admin_flota_required
def ciudad_eliminar(request, pk):
    """
    Solicita confirmación antes de eliminar una ciudad.
    """

    ciudad = get_object_or_404(
        Ciudad,
        pk=pk,
    )

    if request.method == "POST":
        ciudad.delete()

        messages.success(
            request,
            "Ciudad eliminada correctamente."
        )

        return redirect("ciudad_lista")

    return render(
        request,
        "transporte/ciudades/eliminar.html",
        {
            "ciudad": ciudad,
        },
    )


# ==========================================================
# CRUD DE TERMINALES
# ==========================================================


# ==============================
# LISTAR TERMINALES
# ==============================

@admin_flota_required
def terminal_lista(request):
    """
    Muestra todos los terminales registrados junto
    con la ciudad a la que pertenecen.
    """

    terminales = (
        Terminal.objects
        .select_related("ciudad")
        .order_by("ciudad__nombre", "nombre")
    )

    return render(
        request,
        "transporte/terminales/lista.html",
        {
            "terminales": terminales,
        },
    )


# ==============================
# CREAR TERMINAL
# ==============================

@admin_flota_required
def terminal_crear(request):
    """
    Permite registrar un nuevo terminal y asociarlo
    a una ciudad existente.
    """

    if request.method == "POST":
        form = TerminalForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Terminal registrado correctamente."
            )

            return redirect("terminal_lista")

    else:
        form = TerminalForm()

    return render(
        request,
        "transporte/terminales/formulario.html",
        {
            "form": form,
            "titulo": "Registrar terminal",
        },
    )


# ==============================
# EDITAR TERMINAL
# ==============================

@admin_flota_required
def terminal_editar(request, pk):
    """
    Permite modificar los datos de un terminal.
    """

    terminal = get_object_or_404(
        Terminal,
        pk=pk,
    )

    if request.method == "POST":
        form = TerminalForm(
            request.POST,
            instance=terminal,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Terminal actualizado correctamente."
            )

            return redirect("terminal_lista")

    else:
        form = TerminalForm(
            instance=terminal,
        )

    return render(
        request,
        "transporte/terminales/formulario.html",
        {
            "form": form,
            "titulo": "Editar terminal",
            "terminal": terminal,
        },
    )


# ==============================
# ELIMINAR TERMINAL
# ==============================

@admin_flota_required
def terminal_eliminar(request, pk):
    """
    Solicita confirmación antes de eliminar
    un terminal.
    """

    terminal = get_object_or_404(
        Terminal,
        pk=pk,
    )

    if request.method == "POST":
        terminal.delete()

        messages.success(
            request,
            "Terminal eliminado correctamente."
        )

        return redirect("terminal_lista")

    return render(
        request,
        "transporte/terminales/eliminar.html",
        {
            "terminal": terminal,
        },
    )


# ==========================================================
# CRUD DE RUTAS
# ==========================================================


# ==============================
# LISTAR RUTAS
# ==============================

@admin_flota_required
def ruta_lista(request):
    """
    Muestra todas las rutas registradas con sus
    terminales y ciudades de origen y destino.
    """

    rutas = (
        Ruta.objects
        .select_related(
            "terminal_origen",
            "terminal_origen__ciudad",
            "terminal_destino",
            "terminal_destino__ciudad",
        )
        .order_by(
            "terminal_origen__ciudad__nombre",
            "terminal_destino__ciudad__nombre",
        )
    )

    return render(
        request,
        "transporte/rutas/lista.html",
        {
            "rutas": rutas,
        },
    )


# ==============================
# CREAR RUTA
# ==============================

@admin_flota_required
def ruta_crear(request):
    """
    Permite registrar una nueva ruta entre
    dos terminales.
    """

    if request.method == "POST":
        form = RutaForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Ruta registrada correctamente."
            )

            return redirect("ruta_lista")

    else:
        form = RutaForm()

    return render(
        request,
        "transporte/rutas/formulario.html",
        {
            "form": form,
            "titulo": "Registrar ruta",
        },
    )


# ==============================
# EDITAR RUTA
# ==============================

@admin_flota_required
def ruta_editar(request, pk):
    """
    Permite modificar una ruta existente.
    """

    ruta = get_object_or_404(
        Ruta,
        pk=pk,
    )

    if request.method == "POST":
        form = RutaForm(
            request.POST,
            instance=ruta,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Ruta actualizada correctamente."
            )

            return redirect("ruta_lista")

    else:
        form = RutaForm(
            instance=ruta,
        )

    return render(
        request,
        "transporte/rutas/formulario.html",
        {
            "form": form,
            "titulo": "Editar ruta",
            "ruta": ruta,
        },
    )


# ==============================
# ELIMINAR RUTA
# ==============================

@admin_flota_required
def ruta_eliminar(request, pk):
    """
    Solicita confirmación antes de eliminar
    una ruta.
    """

    ruta = get_object_or_404(
        Ruta,
        pk=pk,
    )

    if request.method == "POST":
        ruta.delete()

        messages.success(
            request,
            "Ruta eliminada correctamente."
        )

        return redirect("ruta_lista")

    return render(
        request,
        "transporte/rutas/eliminar.html",
        {
            "ruta": ruta,
        },
    )
# ==========================================================
# CRUD DE BUSES
# ==========================================================


# ==============================
# LISTAR BUSES
# ==============================

@admin_flota_required
def bus_lista(request):
    """
    Muestra todos los buses registrados.
    """

    buses = Bus.objects.all().order_by("numero_bus")

    return render(
        request,
        "transporte/buses/lista.html",
        {
            "buses": buses,
        },
    )


# ==============================
# CREAR BUS
# ==============================

@admin_flota_required
def bus_crear(request):
    """
    Permite registrar un nuevo bus.
    """

    if request.method == "POST":
        form = BusForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Bus registrado correctamente."
            )

            return redirect("bus_lista")

    else:
        form = BusForm()

    return render(
        request,
        "transporte/buses/formulario.html",
        {
            "form": form,
            "titulo": "Registrar bus",
        },
    )


# ==============================
# EDITAR BUS
# ==============================

@admin_flota_required
def bus_editar(request, pk):
    """
    Permite modificar los datos de un bus.
    """

    bus = get_object_or_404(
        Bus,
        pk=pk,
    )

    if request.method == "POST":
        form = BusForm(
            request.POST,
            instance=bus,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Bus actualizado correctamente."
            )

            return redirect("bus_lista")

    else:
        form = BusForm(
            instance=bus,
        )

    return render(
        request,
        "transporte/buses/formulario.html",
        {
            "form": form,
            "titulo": "Editar bus",
            "bus": bus,
        },
    )


# ==============================
# ELIMINAR BUS
# ==============================

@admin_flota_required
def bus_eliminar(request, pk):
    """
    Solicita confirmación antes de eliminar un bus.
    """

    bus = get_object_or_404(
        Bus,
        pk=pk,
    )

    if request.method == "POST":
        bus.delete()

        messages.success(
            request,
            "Bus eliminado correctamente."
        )

        return redirect("bus_lista")

    return render(
        request,
        "transporte/buses/eliminar.html",
        {
            "bus": bus,
        },
    )


# ==========================================================
# CRUD DE ASIENTOS
# ==========================================================


# ==============================
# LISTAR ASIENTOS
# ==============================

@admin_flota_required
def asiento_lista(request):
    """
    Muestra todos los asientos registrados,
    indicando el bus al que pertenecen.
    """

    asientos = (
        Asiento.objects
        .select_related("bus")
        .order_by("bus__numero_bus", "numero")
    )

    return render(
        request,
        "transporte/asientos/lista.html",
        {
            "asientos": asientos,
        },
    )


# ==============================
# CREAR ASIENTO
# ==============================

@admin_flota_required
def asiento_crear(request):
    """
    Permite registrar un nuevo asiento físico
    y asociarlo a un bus.
    """

    if request.method == "POST":
        form = AsientoForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Asiento registrado correctamente."
            )

            return redirect("asiento_lista")

    else:
        form = AsientoForm()

    return render(
        request,
        "transporte/asientos/formulario.html",
        {
            "form": form,
            "titulo": "Registrar asiento",
        },
    )


# ==============================
# EDITAR ASIENTO
# ==============================

@admin_flota_required
def asiento_editar(request, pk):
    """
    Permite modificar los datos de un asiento.
    """

    asiento = get_object_or_404(
        Asiento.objects.select_related("bus"),
        pk=pk,
    )

    if request.method == "POST":
        form = AsientoForm(
            request.POST,
            instance=asiento,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Asiento actualizado correctamente."
            )

            return redirect("asiento_lista")

    else:
        form = AsientoForm(
            instance=asiento,
        )

    return render(
        request,
        "transporte/asientos/formulario.html",
        {
            "form": form,
            "titulo": "Editar asiento",
            "asiento": asiento,
        },
    )


# ==============================
# ELIMINAR ASIENTO
# ==============================

@admin_flota_required
def asiento_eliminar(request, pk):
    """
    Solicita confirmación antes de eliminar
    un asiento.
    """

    asiento = get_object_or_404(
        Asiento.objects.select_related("bus"),
        pk=pk,
    )

    if request.method == "POST":
        asiento.delete()

        messages.success(
            request,
            "Asiento eliminado correctamente."
        )

        return redirect("asiento_lista")

    return render(
        request,
        "transporte/asientos/eliminar.html",
        {
            "asiento": asiento,
        },
    )
# ==========================================================
# CRUD DE SERVICIOS
# ==========================================================


# ==============================
# LISTAR SERVICIOS
# ==============================

@admin_flota_required
def servicio_lista(request):
    """
    Muestra todos los servicios registrados junto con
    la ruta, el bus y la fecha y hora de salida.
    """

    servicios = (
        Servicio.objects
        .select_related(
            "ruta",
            "ruta__terminal_origen",
            "ruta__terminal_origen__ciudad",
            "ruta__terminal_destino",
            "ruta__terminal_destino__ciudad",
            "bus",
        )
        .order_by("fecha_hora_salida")
    )

    return render(
        request,
        "transporte/servicios/lista.html",
        {
            "servicios": servicios,
        },
    )


# ==============================
# CREAR SERVICIO
# ==============================

@admin_flota_required
def servicio_crear(request):
    """
    Permite registrar un nuevo servicio asociando
    una ruta, un bus y una fecha y hora de salida.
    """

    if request.method == "POST":
        form = ServicioForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Servicio registrado correctamente."
            )

            return redirect("servicio_lista")

    else:
        form = ServicioForm()

    return render(
        request,
        "transporte/servicios/formulario.html",
        {
            "form": form,
            "titulo": "Registrar servicio",
        },
    )


# ==============================
# EDITAR SERVICIO
# ==============================

@admin_flota_required
def servicio_editar(request, pk):
    """
    Permite modificar la ruta, el bus,
    la fecha de salida o el estado de un servicio.
    """

    servicio = get_object_or_404(
        Servicio.objects.select_related(
            "ruta",
            "bus",
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = ServicioForm(
            request.POST,
            instance=servicio,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Servicio actualizado correctamente."
            )

            return redirect("servicio_lista")

    else:
        form = ServicioForm(
            instance=servicio,
        )

    return render(
        request,
        "transporte/servicios/formulario.html",
        {
            "form": form,
            "titulo": "Editar servicio",
            "servicio": servicio,
        },
    )


# ==============================
# ELIMINAR SERVICIO
# ==============================

@admin_flota_required
def servicio_eliminar(request, pk):
    """
    Solicita confirmación antes de eliminar
    un servicio.
    """

    servicio = get_object_or_404(
        Servicio.objects.select_related(
            "ruta",
            "ruta__terminal_origen",
            "ruta__terminal_origen__ciudad",
            "ruta__terminal_destino",
            "ruta__terminal_destino__ciudad",
            "bus",
        ),
        pk=pk,
    )

    if request.method == "POST":
        servicio.delete()

        messages.success(
            request,
            "Servicio eliminado correctamente."
        )

        return redirect("servicio_lista")

    return render(
        request,
        "transporte/servicios/eliminar.html",
        {
            "servicio": servicio,
        },
    )


# ==========================================================
# CRUD DE ASIENTOS POR SERVICIO
# ==========================================================


# ==============================
# LISTAR ASIENTOS POR SERVICIO
# ==============================

@admin_flota_required
def asiento_servicio_lista(request):
    """
    Muestra los asientos asociados a los servicios,
    incluyendo tarifa y estado de disponibilidad.
    """

    asientos_servicio = (
        AsientoServicio.objects
        .select_related(
            "servicio",
            "servicio__ruta",
            "servicio__ruta__terminal_origen",
            "servicio__ruta__terminal_origen__ciudad",
            "servicio__ruta__terminal_destino",
            "servicio__ruta__terminal_destino__ciudad",
            "servicio__bus",
            "asiento",
            "asiento__bus",
        )
        .order_by(
            "servicio__fecha_hora_salida",
            "asiento__numero",
        )
    )

    return render(
        request,
        "transporte/asientos_servicio/lista.html",
        {
            "asientos_servicio": asientos_servicio,
        },
    )


# ==============================
# CREAR ASIENTO POR SERVICIO
# ==============================

@admin_flota_required
def asiento_servicio_crear(request):
    """
    Permite asociar un asiento físico a un servicio,
    estableciendo su tarifa y estado.
    """

    if request.method == "POST":
        form = AsientoServicioForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Asiento asociado al servicio correctamente."
            )

            return redirect("asiento_servicio_lista")

    else:
        form = AsientoServicioForm()

    return render(
        request,
        "transporte/asientos_servicio/formulario.html",
        {
            "form": form,
            "titulo": "Asignar asiento a servicio",
        },
    )


# ==============================
# EDITAR ASIENTO POR SERVICIO
# ==============================

@admin_flota_required
def asiento_servicio_editar(request, pk):
    """
    Permite modificar la tarifa o el estado
    de un asiento asociado a un servicio.
    """

    asiento_servicio = get_object_or_404(
        AsientoServicio.objects.select_related(
            "servicio",
            "asiento",
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = AsientoServicioForm(
            request.POST,
            instance=asiento_servicio,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Asiento del servicio actualizado correctamente."
            )

            return redirect("asiento_servicio_lista")

    else:
        form = AsientoServicioForm(
            instance=asiento_servicio,
        )

    return render(
        request,
        "transporte/asientos_servicio/formulario.html",
        {
            "form": form,
            "titulo": "Editar asiento del servicio",
            "asiento_servicio": asiento_servicio,
        },
    )


# ==============================
# ELIMINAR ASIENTO POR SERVICIO
# ==============================

@admin_flota_required
def asiento_servicio_eliminar(request, pk):
    """
    Solicita confirmación antes de eliminar
    un asiento asociado a un servicio.
    """

    asiento_servicio = get_object_or_404(
        AsientoServicio.objects.select_related(
            "servicio",
            "servicio__ruta",
            "servicio__ruta__terminal_origen",
            "servicio__ruta__terminal_origen__ciudad",
            "servicio__ruta__terminal_destino",
            "servicio__ruta__terminal_destino__ciudad",
            "asiento",
            "asiento__bus",
        ),
        pk=pk,
    )

    if request.method == "POST":
        asiento_servicio.delete()

        messages.success(
            request,
            "Asiento eliminado del servicio correctamente."
        )

        return redirect("asiento_servicio_lista")

    return render(
        request,
        "transporte/asientos_servicio/eliminar.html",
        {
            "asiento_servicio": asiento_servicio,
        },
    )
# ==========================================================
# BÚSQUEDA WEB DE PASAJES
# ==========================================================

def buscar_pasajes(request):
    """
    Permite buscar servicios disponibles por ciudad
    de origen, ciudad de destino y fecha de viaje.
    """

    # ======================================================
    # OBTENER PARÁMETROS DE BÚSQUEDA
    # ======================================================

    origen = request.GET.get("origen")
    destino = request.GET.get("destino")
    fecha = request.GET.get("fecha", "")

    # Los parámetros GET llegan como texto.
    # Se convierten los ID de las ciudades a enteros.

    if origen:
        try:
            origen = int(origen)
        except (TypeError, ValueError):
            origen = None

    if destino:
        try:
            destino = int(destino)
        except (TypeError, ValueError):
            destino = None

    # ======================================================
    # OBTENER CIUDADES
    # ======================================================

    ciudades = (
        Ciudad.objects
        .all()
        .order_by("nombre")
    )

    # ======================================================
    # DETERMINAR SI EXISTE UNA BÚSQUEDA
    # ======================================================

    busqueda_realizada = bool(
        origen
        and destino
        and fecha
    )

    # ======================================================
    # CONSULTA BASE
    # ======================================================

    servicios = Servicio.objects.none()

    # Solamente se consultan servicios cuando el usuario
    # seleccionó origen, destino y fecha.

    if busqueda_realizada:

        servicios = (
            Servicio.objects
            .filter(
                activo=True,
                ruta__activa=True,
                bus__activo=True,
                ruta__terminal_origen__ciudad_id=origen,
                ruta__terminal_destino__ciudad_id=destino,
                fecha_hora_salida__date=fecha,
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

    # ======================================================
    # PREPARAR RESULTADOS
    # ======================================================

    resultados = []

    for servicio in servicios:

        asientos_disponibles = (
            servicio.asientos_servicio
            .filter(
                estado="DISPONIBLE"
            )
            .count()
        )

        resultados.append(
            {
                "servicio": servicio,
                "asientos_disponibles": asientos_disponibles,
            }
        )

    # ======================================================
    # MOSTRAR PÁGINA
    # ======================================================

    return render(
        request,
        "transporte/pasajeros/buscar_pasajes.html",
        {
            "ciudades": ciudades,
            "resultados": resultados,
            "origen_seleccionado": origen,
            "destino_seleccionado": destino,
            "fecha_seleccionada": fecha,
            "busqueda_realizada": busqueda_realizada,
        },
    )
# ==========================================================
# SELECCIÓN WEB DE ASIENTOS
# ==========================================================

def seleccionar_asientos(request, servicio_id):
    """
    Muestra la información de un servicio y los asientos
    disponibles u ocupados para que el pasajero pueda
    seleccionar uno.
    """

    # ======================================================
    # OBTENER SERVICIO
    # ======================================================

    servicio = get_object_or_404(
        Servicio.objects.select_related(
            "ruta",
            "ruta__terminal_origen",
            "ruta__terminal_origen__ciudad",
            "ruta__terminal_destino",
            "ruta__terminal_destino__ciudad",
            "bus",
        ),
        pk=servicio_id,
        activo=True,
    )

    # ======================================================
    # OBTENER ASIENTOS DEL SERVICIO
    # ======================================================

    asientos = (
        AsientoServicio.objects
        .filter(
            servicio=servicio
        )
        .select_related(
            "asiento",
            "asiento__bus",
        )
        .order_by(
            "asiento__numero"
        )
    )

    # ======================================================
    # MOSTRAR PÁGINA
    # ======================================================

    return render(
        request,
        "transporte/pasajeros/seleccionar_asientos.html",
        {
            "servicio": servicio,
            "asientos": asientos,
        },
    )
