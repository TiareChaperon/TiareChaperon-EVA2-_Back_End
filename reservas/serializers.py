from rest_framework import serializers

from transporte.models import AsientoServicio

from .models import CarroPasajes, ItemCarro


# ==========================================================
# SERIALIZER DE ITEM DEL CARRO
# ==========================================================

class ItemCarroSerializer(serializers.ModelSerializer):
    """
    Representa un pasaje agregado al carro.

    Incluye información del asiento y del servicio
    para facilitar su visualización al pasajero.
    """

    numero_asiento = serializers.IntegerField(
        source="asiento_servicio.asiento.numero",
        read_only=True,
    )

    tipo_asiento = serializers.CharField(
        source="asiento_servicio.asiento.get_tipo_display",
        read_only=True,
    )

    tarifa = serializers.DecimalField(
        source="asiento_servicio.tarifa",
        max_digits=10,
        decimal_places=2,
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

    fecha_hora_salida = serializers.DateTimeField(
        source="asiento_servicio.servicio.fecha_hora_salida",
        read_only=True,
    )

    numero_bus = serializers.CharField(
        source="asiento_servicio.servicio.bus.numero_bus",
        read_only=True,
    )

    class Meta:
        model = ItemCarro

        fields = [
            "id",
            "asiento_servicio",
            "numero_asiento",
            "tipo_asiento",
            "tarifa",
            "origen",
            "destino",
            "fecha_hora_salida",
            "numero_bus",
            "nombre_ocupante",
            "documento_ocupante",
            "agregado",
        ]

        read_only_fields = [
            "id",
            "agregado",
        ]

    def validate_asiento_servicio(self, asiento_servicio):
        """
        Impide agregar al carro un asiento que ya
        se encuentre ocupado.
        """

        if asiento_servicio.estado == "OCUPADO":
            raise serializers.ValidationError(
                "El asiento seleccionado ya se encuentra ocupado."
            )

        return asiento_servicio


# ==========================================================
# SERIALIZER DEL CARRO
# ==========================================================

class CarroPasajesSerializer(serializers.ModelSerializer):
    """
    Representa el carro persistente de un pasajero
    junto con todos los pasajes agregados.
    """

    items = ItemCarroSerializer(
        many=True,
        read_only=True,
    )

    total = serializers.SerializerMethodField()

    def get_total(self, obj):
        """
        Calcula el total actual del carro utilizando
        las tarifas de los asientos seleccionados.
        """

        return sum(
            item.asiento_servicio.tarifa
            for item in obj.items.all()
        )

    class Meta:
        model = CarroPasajes

        fields = [
            "id",
            "estado",
            "creado",
            "actualizado",
            "items",
            "total",
        ]

        read_only_fields = [
            "id",
            "estado",
            "creado",
            "actualizado",
            "items",
            "total",
        ]
