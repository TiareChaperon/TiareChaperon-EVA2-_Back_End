import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from reservas.models import CarroPasajes
from transporte.models import AsientoServicio

from .models import Boleto, DetalleVenta, Venta


# ==========================================================
# CHECKOUT WEB
# ==========================================================

@login_required
def checkout_web(request):
    """
    Procesa el pago del carro del pasajero.

    Antes de confirmar la compra se bloquean y verifican
    nuevamente los asientos mediante una transacción
    atómica para evitar ventas simultáneas del mismo asiento.
    """

    # ======================================================
    # VERIFICAR ROL
    # ======================================================

    if request.user.role != "PASAJERO":
        messages.error(
            request,
            "Solo los pasajeros pueden realizar compras."
        )
        return redirect("inicio")


    # ======================================================
    # SOLO PERMITIR POST
    # ======================================================

    if request.method != "POST":
        return redirect("ver_carro")


    # ======================================================
    # TRANSACCIÓN ATÓMICA
    # ======================================================

    with transaction.atomic():

        # ==================================================
        # BLOQUEAR CARRO
        # ==================================================

        try:
            carro = (
                CarroPasajes.objects
                .select_for_update()
                .get(
                    usuario=request.user,
                    estado="ACTIVO",
                )
            )

        except CarroPasajes.DoesNotExist:
            messages.error(
                request,
                "No tienes un carro activo."
            )
            return redirect("ver_carro")


        # ==================================================
        # OBTENER ITEMS
        # ==================================================

        items = list(
            carro.items
            .select_related(
                "asiento_servicio",
                "asiento_servicio__asiento",
                "asiento_servicio__servicio",
            )
            .all()
        )


        if not items:
            messages.warning(
                request,
                "Tu carro está vacío."
            )
            return redirect("ver_carro")


        # ==================================================
        # OBTENER IDS DE ASIENTOS
        # ==================================================

        ids_asientos = [
            item.asiento_servicio_id
            for item in items
        ]


        # ==================================================
        # BLOQUEAR ASIENTOS
        # ==================================================

        asientos_bloqueados = list(
            AsientoServicio.objects
            .select_for_update()
            .select_related(
                "asiento",
                "servicio",
            )
            .filter(
                id__in=ids_asientos
            )
            .order_by("id")
        )


        # ==================================================
        # VERIFICAR QUE TODOS EXISTAN
        # ==================================================

        if len(asientos_bloqueados) != len(ids_asientos):
            messages.error(
                request,
                "No fue posible verificar todos los asientos."
            )
            return redirect("ver_carro")


        # ==================================================
        # VERIFICAR DISPONIBILIDAD
        # ==================================================

        for asiento in asientos_bloqueados:

            if asiento.estado != "DISPONIBLE":
                messages.error(
                    request,
                    (
                        f"El asiento {asiento.asiento.numero} "
                        "ya no se encuentra disponible."
                    ),
                )
                return redirect("ver_carro")


        # ==================================================
        # CALCULAR TOTAL
        # ==================================================

        mapa_asientos = {
            asiento.id: asiento
            for asiento in asientos_bloqueados
        }


        total = sum(
            mapa_asientos[
                item.asiento_servicio_id
            ].tarifa
            for item in items
        )


        # ==================================================
        # CREAR VENTA PAGADA
        # ==================================================

        venta = Venta.objects.create(
            usuario=request.user,
            estado="PAGADO",
            total=total,
            fecha_pago=timezone.now(),
        )


        # ==================================================
        # CREAR DETALLES Y BOLETOS
        # ==================================================

        for item in items:

            asiento_servicio = mapa_asientos[
                item.asiento_servicio_id
            ]


            detalle = DetalleVenta.objects.create(
                venta=venta,
                asiento_servicio=asiento_servicio,
                nombre_ocupante=item.nombre_ocupante,
                documento_ocupante=item.documento_ocupante,
                precio=asiento_servicio.tarifa,
            )


            Boleto.objects.create(
                detalle_venta=detalle,
            )


            # ==============================================
            # MARCAR ASIENTO COMO OCUPADO
            # ==============================================

            asiento_servicio.estado = "OCUPADO"

            asiento_servicio.save(
                update_fields=["estado"]
            )


        # ==================================================
        # VACIAR CARRO
        # ==================================================

        carro.items.all().delete()

        carro.estado = "ACTIVO"

        carro.save(
            update_fields=[
                "estado",
                "actualizado",
            ]
        )


    # ======================================================
    # COMPRA EXITOSA
    # ======================================================

    return redirect(
        "compra_exitosa",
        venta_id=venta.id,
    )


# ==========================================================
# COMPRA EXITOSA
# ==========================================================

@login_required
def compra_exitosa(request, venta_id):
    """
    Muestra el resumen de una compra realizada y
    los boletos emitidos.
    """

    if request.user.role != "PASAJERO":
        messages.error(
            request,
            "Solo los pasajeros pueden consultar sus compras."
        )
        return redirect("inicio")


    try:
        venta = (
            Venta.objects
            .prefetch_related(
                "detalles",
                "detalles__boleto",
                "detalles__asiento_servicio",
                "detalles__asiento_servicio__asiento",
                "detalles__asiento_servicio__servicio",
                "detalles__asiento_servicio__servicio__ruta",
                "detalles__asiento_servicio__servicio__ruta__terminal_origen",
                "detalles__asiento_servicio__servicio__ruta__terminal_origen__ciudad",
                "detalles__asiento_servicio__servicio__ruta__terminal_destino",
                "detalles__asiento_servicio__servicio__ruta__terminal_destino__ciudad",
                "detalles__asiento_servicio__servicio__bus",
            )
            .get(
                pk=venta_id,
                usuario=request.user,
            )
        )

    except Venta.DoesNotExist:
        messages.error(
            request,
            "La compra solicitada no existe."
        )
        return redirect("inicio")


    return render(
        request,
        "ventas/compra_exitosa.html",
        {
            "venta": venta,
        },
    )


# ==========================================================
# MIS BOLETOS
# ==========================================================

@login_required
def mis_boletos(request):
    """
    Muestra las compras y boletos del pasajero autenticado.
    """

    # ======================================================
    # VERIFICAR ROL
    # ======================================================

    if request.user.role != "PASAJERO":
        messages.error(
            request,
            "Solo los pasajeros pueden consultar sus boletos."
        )
        return redirect("inicio")


    # ======================================================
    # OBTENER VENTAS DEL PASAJERO
    # ======================================================

    ventas = (
        Venta.objects
        .filter(
            usuario=request.user,
            estado__in=[
                "PAGADO",
                "COMPLETADO",
            ],
        )
        .prefetch_related(
            "detalles",
            "detalles__boleto",
            "detalles__asiento_servicio",
            "detalles__asiento_servicio__asiento",
            "detalles__asiento_servicio__servicio",
            "detalles__asiento_servicio__servicio__ruta",
            "detalles__asiento_servicio__servicio__ruta__terminal_origen",
            "detalles__asiento_servicio__servicio__ruta__terminal_origen__ciudad",
            "detalles__asiento_servicio__servicio__ruta__terminal_destino",
            "detalles__asiento_servicio__servicio__ruta__terminal_destino__ciudad",
            "detalles__asiento_servicio__servicio__bus",
        )
        .order_by("-fecha_creacion")
    )


    # ======================================================
    # MOSTRAR PÁGINA
    # ======================================================

    return render(
        request,
        "ventas/mis_boletos.html",
        {
            "ventas": ventas,
        },
    )


# ==========================================================
# VALIDAR BOLETO
# ==========================================================

@login_required
def validar_boleto(request):

    boleto = None
    codigo = ""
    buscado = False

    # ======================================================
    # VERIFICAR ROL
    # ======================================================

    if request.user.role != "ADMIN_FLOTA":
        messages.error(
            request,
            "Solo el administrador de flota puede validar boletos."
        )
        return redirect("inicio")

    # ======================================================
    # OBTENER CÓDIGO
    # ======================================================

    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        accion = request.POST.get("accion")
    else:
        codigo = request.GET.get("codigo", "").strip()
        accion = None

    # ======================================================
    # BUSCAR BOLETO
    # ======================================================

    if codigo:

        buscado = True

        try:

            codigo_uuid = uuid.UUID(codigo)

            boleto = (
                Boleto.objects
                .select_related(
                    "detalle_venta",
                    "detalle_venta__venta",
                    "detalle_venta__venta__usuario",
                    "detalle_venta__asiento_servicio",
                    "detalle_venta__asiento_servicio__asiento",
                    "detalle_venta__asiento_servicio__servicio",
                    "detalle_venta__asiento_servicio__servicio__bus",
                    "detalle_venta__asiento_servicio__servicio__ruta",
                    "detalle_venta__asiento_servicio__servicio__ruta__terminal_origen",
                    "detalle_venta__asiento_servicio__servicio__ruta__terminal_origen__ciudad",
                    "detalle_venta__asiento_servicio__servicio__ruta__terminal_destino",
                    "detalle_venta__asiento_servicio__servicio__ruta__terminal_destino__ciudad",
                )
                .get(codigo=codigo_uuid)
            )

        except (ValueError, AttributeError, Boleto.DoesNotExist):
            boleto = None

    # ======================================================
    # CONFIRMAR USO DEL BOLETO
    # ======================================================

    if (
        request.method == "POST"
        and accion == "usar"
        and boleto is not None
    ):

        # --------------------------------------------------
        # VERIFICAR ESTADO DE LA VENTA
        # --------------------------------------------------

        if boleto.detalle_venta.venta.estado not in [
            "PAGADO",
            "COMPLETADO",
        ]:

            messages.error(
                request,
                "El boleto no pertenece a una compra válida."
            )

            return redirect(
                f"{request.path}?codigo={boleto.codigo}"
            )

        # --------------------------------------------------
        # EVITAR DOBLE UTILIZACIÓN
        # --------------------------------------------------

        if boleto.utilizado:

            messages.warning(
                request,
                "Este boleto ya había sido utilizado."
            )

            return redirect(
                f"{request.path}?codigo={boleto.codigo}"
            )

        # --------------------------------------------------
        # MARCAR COMO UTILIZADO
        # --------------------------------------------------

        boleto.utilizado = True
        boleto.fecha_utilizacion = timezone.now()

        boleto.save(
            update_fields=[
                "utilizado",
                "fecha_utilizacion",
            ]
        )

        messages.success(
            request,
            "Boleto utilizado correctamente."
        )

        return redirect(
            f"{request.path}?codigo={boleto.codigo}"
        )

    # ======================================================
    # MOSTRAR PÁGINA
    # ======================================================

    return render(
        request,
        "ventas/validar_boleto.html",
        {
            "boleto": boleto,
            "codigo": codigo,
            "buscado": buscado,
        },
    )
