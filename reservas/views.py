from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from transporte.models import AsientoServicio

from .models import CarroPasajes, ItemCarro


# ==========================================================
# AGREGAR ASIENTO AL CARRO
# ==========================================================

@login_required
def agregar_al_carro(request):
    """
    Agrega un asiento al carro persistente del pasajero.

    El asiento NO cambia a OCUPADO al agregarlo al carro.
    La ocupación definitiva se realiza durante el checkout.
    """

    # ======================================================
    # VERIFICAR ROL
    # ======================================================

    if request.user.role != "PASAJERO":
        messages.error(
            request,
            "Solo los pasajeros pueden agregar pasajes al carro."
        )
        return redirect("inicio")

    # ======================================================
    # SOLO PERMITIR POST
    # ======================================================

    if request.method != "POST":
        return redirect("buscar_pasajes")

    # ======================================================
    # OBTENER DATOS DEL FORMULARIO
    # ======================================================

    asiento_servicio_id = request.POST.get("asiento_servicio")
    nombre_ocupante = request.POST.get(
        "nombre_ocupante",
        ""
    ).strip()
    documento_ocupante = request.POST.get(
        "documento_ocupante",
        ""
    ).strip()

    # ======================================================
    # VALIDAR ASIENTO
    # ======================================================

    if not asiento_servicio_id:
        messages.error(
            request,
            "Debes seleccionar un asiento."
        )
        return redirect("buscar_pasajes")

    asiento_servicio = get_object_or_404(
        AsientoServicio.objects.select_related(
            "servicio",
            "asiento",
        ),
        pk=asiento_servicio_id,
    )

    # ======================================================
    # VALIDAR DATOS DEL PASAJERO
    # ======================================================

    if not nombre_ocupante or not documento_ocupante:
        messages.error(
            request,
            "Debes ingresar el nombre y documento del pasajero."
        )
        return redirect(
            "seleccionar_asientos",
            servicio_id=asiento_servicio.servicio_id,
        )

    # ======================================================
    # VERIFICAR DISPONIBILIDAD
    # ======================================================

    if asiento_servicio.estado != "DISPONIBLE":
        messages.error(
            request,
            "El asiento seleccionado ya no está disponible."
        )
        return redirect(
            "seleccionar_asientos",
            servicio_id=asiento_servicio.servicio_id,
        )

    # ======================================================
    # OBTENER O CREAR CARRO
    # ======================================================

    carro, creado = CarroPasajes.objects.get_or_create(
        usuario=request.user,
        defaults={
            "estado": "ACTIVO",
        },
    )

    if carro.estado != "ACTIVO":
        messages.error(
            request,
            "Tu carro de pasajes no se encuentra activo."
        )
        return redirect("buscar_pasajes")

    # ======================================================
    # EVITAR DUPLICADOS
    # ======================================================

    if ItemCarro.objects.filter(
        carro=carro,
        asiento_servicio=asiento_servicio,
    ).exists():
        messages.warning(
            request,
            "Ese asiento ya se encuentra en tu carro."
        )
        return redirect("ver_carro")

    # ======================================================
    # CREAR ITEM
    # ======================================================

    ItemCarro.objects.create(
        carro=carro,
        asiento_servicio=asiento_servicio,
        nombre_ocupante=nombre_ocupante,
        documento_ocupante=documento_ocupante,
    )

    messages.success(
        request,
        (
            f"Asiento {asiento_servicio.asiento.numero} "
            "agregado correctamente al carro."
        ),
    )

    return redirect("ver_carro")


# ==========================================================
# VER CARRO
# ==========================================================

@login_required
def ver_carro(request):
    """
    Muestra el carro persistente del pasajero.
    """

    # ======================================================
    # VERIFICAR ROL
    # ======================================================

    if request.user.role != "PASAJERO":
        messages.error(
            request,
            "Solo los pasajeros pueden acceder al carro."
        )
        return redirect("inicio")

    # ======================================================
    # OBTENER O CREAR CARRO
    # ======================================================

    carro, creado = CarroPasajes.objects.get_or_create(
        usuario=request.user,
        defaults={
            "estado": "ACTIVO",
        },
    )

    # ======================================================
    # OBTENER ITEMS
    # ======================================================

    items = (
        carro.items
        .select_related(
            "asiento_servicio",
            "asiento_servicio__asiento",
            "asiento_servicio__servicio",
            "asiento_servicio__servicio__ruta",
            "asiento_servicio__servicio__ruta__terminal_origen",
            "asiento_servicio__servicio__ruta__terminal_origen__ciudad",
            "asiento_servicio__servicio__ruta__terminal_destino",
            "asiento_servicio__servicio__ruta__terminal_destino__ciudad",
            "asiento_servicio__servicio__bus",
        )
        .order_by("agregado")
    )

    # ======================================================
    # CALCULAR TOTAL
    # ======================================================

    total = sum(
        item.asiento_servicio.tarifa
        for item in items
    )

    return render(
        request,
        "reservas/carro.html",
        {
            "carro": carro,
            "items": items,
            "total": total,
        },
    )


# ==========================================================
# ELIMINAR ITEM DEL CARRO
# ==========================================================

@login_required
def eliminar_del_carro(request, item_id):
    """
    Elimina un pasaje del carro del usuario autenticado.

    Como el asiento todavía no fue pagado, su estado
    permanece DISPONIBLE.
    """

    # ======================================================
    # VERIFICAR ROL
    # ======================================================

    if request.user.role != "PASAJERO":
        messages.error(
            request,
            "Solo los pasajeros pueden modificar el carro."
        )
        return redirect("inicio")

    # ======================================================
    # SOLO PERMITIR POST
    # ======================================================

    if request.method != "POST":
        return redirect("ver_carro")

    # ======================================================
    # BUSCAR ITEM DEL CARRO DEL USUARIO
    # ======================================================

    item = get_object_or_404(
        ItemCarro.objects.select_related(
            "carro",
            "asiento_servicio",
            "asiento_servicio__asiento",
        ),
        pk=item_id,
        carro__usuario=request.user,
    )

    numero_asiento = item.asiento_servicio.asiento.numero

    # ======================================================
    # ELIMINAR
    # ======================================================

    item.delete()

    messages.success(
        request,
        f"Asiento {numero_asiento} eliminado del carro."
    )

    return redirect("ver_carro")
