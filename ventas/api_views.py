from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import (
    IsAdministradorFlota,
    IsPasajero,
)
from reservas.models import CarroPasajes
from transporte.models import AsientoServicio

from .models import Boleto, DetalleVenta, Venta
from .serializers import VentaSerializer


# ==========================================================
# CHECKOUT DE VENTA
# ==========================================================

class CheckoutView(APIView):
    """
    Procesa la compra de los pasajes almacenados
    en el carro del pasajero.

    La operación se ejecuta dentro de una transacción
    atómica para evitar ventas parciales.
    """

    permission_classes = [IsPasajero]

    def post(self, request):
        """
        Verifica nuevamente la disponibilidad de todos
        los asientos antes de concretar la venta.
        """

        try:

            # ==================================================
            # TRANSACCIÓN ATÓMICA
            # ==================================================

            with transaction.atomic():

                # ==============================================
                # OBTENER CARRO DEL PASAJERO
                # ==============================================

                try:
                    carro = (
                        CarroPasajes.objects
                        .select_for_update()
                        .prefetch_related(
                            "items__asiento_servicio"
                        )
                        .get(
                            usuario=request.user,
                            estado="ACTIVO",
                        )
                    )

                except CarroPasajes.DoesNotExist:
                    return Response(
                        {
                            "detail": (
                                "No existe un carro activo "
                                "para este pasajero."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                items = list(
                    carro.items.all()
                )

                # ==============================================
                # VALIDAR QUE EL CARRO NO ESTÉ VACÍO
                # ==============================================

                if not items:
                    return Response(
                        {
                            "detail": (
                                "El carro de pasajes está vacío."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # ==============================================
                # OBTENER IDS DE LOS ASIENTOS
                # ==============================================

                ids_asientos = [
                    item.asiento_servicio_id
                    for item in items
                ]

                # ==============================================
                # BLOQUEAR LOS ASIENTOS
                # ==============================================

                asientos_bloqueados = list(
                    AsientoServicio.objects
                    .select_for_update()
                    .filter(
                        id__in=ids_asientos
                    )
                    .select_related(
                        "asiento",
                        "servicio",
                    )
                    .order_by("id")
                )

                # ==============================================
                # VERIFICAR DISPONIBILIDAD
                # ==============================================

                for asiento_servicio in asientos_bloqueados:

                    if asiento_servicio.estado != "DISPONIBLE":
                        return Response(
                            {
                                "detail": (
                                    "Uno de los asientos "
                                    "seleccionados ya no "
                                    "se encuentra disponible."
                                ),
                                "asiento": (
                                    asiento_servicio.asiento.numero
                                ),
                            },
                            status=status.HTTP_409_CONFLICT,
                        )

                # ==============================================
                # CALCULAR TOTAL
                # ==============================================

                total = sum(
                    asiento.tarifa
                    for asiento in asientos_bloqueados
                )

                # ==============================================
                # CREAR VENTA
                # ==============================================

                venta = Venta.objects.create(
                    usuario=request.user,
                    estado="PAGADO",
                    total=total,
                    fecha_pago=timezone.now(),
                )

                # ==============================================
                # MAPA DE ASIENTOS BLOQUEADOS
                # ==============================================

                mapa_asientos = {
                    asiento.id: asiento
                    for asiento in asientos_bloqueados
                }

                # ==============================================
                # CREAR DETALLES Y BOLETOS
                # ==============================================

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
                        detalle_venta=detalle
                    )

                    # El asiento solamente pasa a OCUPADO
                    # cuando la venta queda PAGADA.
                    asiento_servicio.estado = "OCUPADO"

                    asiento_servicio.save(
                        update_fields=[
                            "estado",
                        ]
                    )

                # ==============================================
                # VACIAR Y REACTIVAR EL CARRO
                # ==============================================

                # Los items ya fueron transferidos a la venta.
                carro.items.all().delete()

                # El carro es persistente y existe uno
                # por pasajero. Después de la compra queda
                # disponible para futuras reservas.
                carro.estado = "ACTIVO"

                carro.save(
                    update_fields=[
                        "estado",
                        "actualizado",
                    ]
                )

            # ==================================================
            # RECUPERAR VENTA COMPLETA
            # ==================================================

            venta = (
                Venta.objects
                .prefetch_related(
                    "detalles__boleto",
                    "detalles__asiento_servicio__asiento",
                    (
                        "detalles__asiento_servicio__servicio__"
                        "ruta__terminal_origen__ciudad"
                    ),
                    (
                        "detalles__asiento_servicio__servicio__"
                        "ruta__terminal_destino__ciudad"
                    ),
                )
                .get(
                    pk=venta.pk
                )
            )

            # ==================================================
            # SERIALIZAR RESPUESTA
            # ==================================================

            serializer = VentaSerializer(
                venta
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as error:

            return Response(
                {
                    "detail": (
                        "No fue posible procesar "
                        "la compra."
                    ),
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==========================================================
# MIS BOLETOS
# ==========================================================

class MisBoletosView(APIView):
    """
    Permite al pasajero autenticado consultar
    todos los boletos asociados a sus compras.
    """

    permission_classes = [IsPasajero]

    def get(self, request):
        """
        Obtiene únicamente las ventas pertenecientes
        al pasajero autenticado.
        """

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
                "detalles__boleto",
                "detalles__asiento_servicio__asiento",
                (
                    "detalles__asiento_servicio__servicio__"
                    "ruta__terminal_origen__ciudad"
                ),
                (
                    "detalles__asiento_servicio__servicio__"
                    "ruta__terminal_destino__ciudad"
                ),
            )
            .order_by(
                "-fecha_creacion"
            )
        )

        serializer = VentaSerializer(
            ventas,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CAMBIO DE ESTADO DE UNA VENTA
# ==========================================================

class CambiarEstadoVentaView(APIView):
    """
    Permite al Administrador de Flota cambiar
    el estado de una venta.

    Si una venta se cancela antes de la salida,
    sus asientos vuelven a quedar disponibles.
    """

    permission_classes = [IsAdministradorFlota]

    def patch(self, request, pk):
        """
        Cambia el estado de una venta.
        """

        nuevo_estado = request.data.get("estado")

        # ==============================================
        # VALIDAR ESTADO SOLICITADO
        # ==============================================

        estados_permitidos = [
            "PAGADO",
            "COMPLETADO",
            "CANCELADO",
        ]

        if nuevo_estado not in estados_permitidos:
            return Response(
                {
                    "detail": (
                        "El estado indicado no es válido."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            # ==============================================
            # TRANSACCIÓN ATÓMICA
            # ==============================================

            with transaction.atomic():

                # ==========================================
                # BLOQUEAR Y OBTENER VENTA
                # ==========================================

                try:
                    venta = (
                        Venta.objects
                        .select_for_update()
                        .get(pk=pk)
                    )

                except Venta.DoesNotExist:
                    return Response(
                        {
                            "detail": (
                                "La venta no existe."
                            )
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # ==========================================
                # EVITAR MODIFICAR UNA VENTA CANCELADA
                # ==========================================

                if venta.estado == "CANCELADO":
                    return Response(
                        {
                            "detail": (
                                "La venta ya se encuentra "
                                "cancelada."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # ==========================================
                # PROCESAR CANCELACIÓN
                # ==========================================

                if nuevo_estado == "CANCELADO":

                    detalles = list(
                        venta.detalles
                        .select_related(
                            "asiento_servicio__servicio"
                        )
                        .all()
                    )

                    # ======================================
                    # VALIDAR FECHA DE SALIDA
                    # ======================================

                    for detalle in detalles:

                        fecha_salida = (
                            detalle
                            .asiento_servicio
                            .servicio
                            .fecha_hora_salida
                        )

                        if fecha_salida <= timezone.now():
                            return Response(
                                {
                                    "detail": (
                                        "No se puede cancelar "
                                        "la venta porque el viaje "
                                        "ya comenzó o finalizó."
                                    )
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    # ======================================
                    # OBTENER IDS DE ASIENTOS
                    # ======================================

                    ids_asientos = [
                        detalle.asiento_servicio_id
                        for detalle in detalles
                    ]

                    # ======================================
                    # BLOQUEAR ASIENTOS
                    # ======================================

                    asientos = list(
                        AsientoServicio.objects
                        .select_for_update()
                        .filter(
                            id__in=ids_asientos
                        )
                        .order_by("id")
                    )

                    # ======================================
                    # LIBERAR ASIENTOS
                    # ======================================

                    for asiento in asientos:

                        asiento.estado = "DISPONIBLE"

                        asiento.save(
                            update_fields=[
                                "estado",
                            ]
                        )

                    # ======================================
                    # CANCELAR VENTA
                    # ======================================

                    venta.estado = "CANCELADO"
                    venta.fecha_cancelacion = timezone.now()

                    venta.save(
                        update_fields=[
                            "estado",
                            "fecha_cancelacion",
                        ]
                    )

                # ==========================================
                # OTROS CAMBIOS DE ESTADO
                # ==========================================

                else:

                    venta.estado = nuevo_estado

                    venta.save(
                        update_fields=[
                            "estado",
                        ]
                    )

            # ==============================================
            # RECUPERAR VENTA COMPLETA
            # ==============================================

            venta = (
                Venta.objects
                .prefetch_related(
                    "detalles__boleto",
                    "detalles__asiento_servicio__asiento",
                    (
                        "detalles__asiento_servicio__servicio__"
                        "ruta__terminal_origen__ciudad"
                    ),
                    (
                        "detalles__asiento_servicio__servicio__"
                        "ruta__terminal_destino__ciudad"
                    ),
                )
                .get(
                    pk=venta.pk
                )
            )

            # ==============================================
            # RESPUESTA
            # ==============================================

            serializer = VentaSerializer(
                venta
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        except Exception as error:

            return Response(
                {
                    "detail": (
                        "No fue posible actualizar "
                        "el estado de la venta."
                    ),
                    "error": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
