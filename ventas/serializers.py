from rest_framework import serializers

from .models import Boleto, DetalleVenta, Venta


# ==========================================================
# SERIALIZER DE BOLETO
# ==========================================================

class BoletoSerializer(serializers.ModelSerializer):
    """
    Representa el boleto emitido después de que
    una venta ha sido pagada correctamente.
    """

    class Meta:
        model = Boleto

        fields = [
            "id",
            "codigo",
            "fecha_emision",
            "utilizado",
            "fecha_utilizacion",
        ]

        read_only_fields = fields

# ==========================================================
# SERIALIZER DE DETALLE DE VENTA
# ==========================================================

class DetalleVentaSerializer(serializers.ModelSerializer):
    """
    Representa cada pasaje incluido dentro de una venta.
    """

    numero_asiento = serializers.IntegerField(
        source="asiento_servicio.asiento.numero",
        read_only=True,
    )

    tipo_asiento = serializers.CharField(
        source="asiento_servicio.asiento.get_tipo_display",
        read_only=True,
    )

    origen = serializers.CharField(
        source=(
            "asiento_servicio.servicio."
            "ruta.terminal_origen.ciudad.nombre"
        ),
        read_only=True,
    )

    destino = serializers.CharField(
        source=(
            "asiento_servicio.servicio."
            "ruta.terminal_destino.ciudad.nombre"
        ),
        read_only=True,
    )

    boleto = BoletoSerializer(
        read_only=True,
    )

    class Meta:
        model = DetalleVenta

        fields = [
            "id",
            "asiento_servicio",
            "numero_asiento",
            "tipo_asiento",
            "origen",
            "destino",
            "nombre_ocupante",
            "documento_ocupante",
            "precio",
            "boleto",
        ]

        read_only_fields = fields


# ==========================================================
# SERIALIZER DE VENTA
# ==========================================================

class VentaSerializer(serializers.ModelSerializer):
    """
    Representa una venta junto con todos sus
    pasajes y boletos emitidos.
    """

    detalles = DetalleVentaSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Venta

        fields = [
            "id",
            "estado",
            "total",
            "fecha_creacion",
            "fecha_pago",
            "fecha_cancelacion",
            "detalles",
        ]

        read_only_fields = fields
