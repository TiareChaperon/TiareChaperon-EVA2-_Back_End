from rest_framework import serializers

from .models import AsientoServicio, Servicio


# ==============================
# SERIALIZER PÚBLICO DE SERVICIOS
# ==============================

class ServicioSerializer(serializers.ModelSerializer):
    """
    Transforma un servicio en una representación JSON
    adecuada para la búsqueda pública de pasajes.

    Los datos de origen y destino se obtienen mediante
    las relaciones normalizadas del modelo.
    """

    ciudad_origen = serializers.CharField(
        source="ruta.terminal_origen.ciudad.nombre",
        read_only=True,
    )

    terminal_origen = serializers.CharField(
        source="ruta.terminal_origen.nombre",
        read_only=True,
    )

    ciudad_destino = serializers.CharField(
        source="ruta.terminal_destino.ciudad.nombre",
        read_only=True,
    )

    terminal_destino = serializers.CharField(
        source="ruta.terminal_destino.nombre",
        read_only=True,
    )

    numero_bus = serializers.CharField(
        source="bus.numero_bus",
        read_only=True,
    )

    asientos_disponibles = serializers.SerializerMethodField()


    # ==============================
    # CANTIDAD DE ASIENTOS DISPONIBLES
    # ==============================

    def get_asientos_disponibles(self, obj):
        """
        Cuenta los asientos que continúan disponibles
        para el servicio consultado.
        """

        return obj.asientos_servicio.filter(
            estado="DISPONIBLE"
        ).count()


    class Meta:

        model = Servicio

        fields = [
            "id",
            "ciudad_origen",
            "terminal_origen",
            "ciudad_destino",
            "terminal_destino",
            "fecha_hora_salida",
            "numero_bus",
            "asientos_disponibles",
        ]
# ==============================
# SERIALIZER DE ASIENTOS
# POR SERVICIO
# ==============================

class AsientoServicioSerializer(serializers.ModelSerializer):
    """
    Convierte los asientos asociados a un servicio
    en información JSON para la API pública.
    """

    numero = serializers.IntegerField(
        source="asiento.numero",
        read_only=True,
    )

    tipo = serializers.CharField(
        source="asiento.tipo",
        read_only=True,
    )

    tipo_nombre = serializers.CharField(
        source="asiento.get_tipo_display",
        read_only=True,
    )

    numero_bus = serializers.CharField(
        source="servicio.bus.numero_bus",
        read_only=True,
    )

    class Meta:
        model = AsientoServicio

        fields = [
            "id",
            "numero",
            "tipo",
            "tipo_nombre",
            "tarifa",
            "estado",
            "numero_bus",
        ]
# ==========================================================
# SERIALIZER ADMINISTRATIVO DE SERVICIO
# ==========================================================

class ServicioAdminSerializer(serializers.ModelSerializer):
    """
    Serializer utilizado por el Administrador de Flota
    para crear y modificar servicios.
    """

    class Meta:
        model = Servicio

        fields = [
            "id",
            "ruta",
            "bus",
            "fecha_hora_salida",
            "activo",
        ]

        read_only_fields = [
            "id",
        ]

    # ======================================================
    # VALIDACIÓN GENERAL DEL SERVICIO
    # ======================================================

    def validate(self, attrs):
        """
        Valida que la ruta y el bus seleccionados
        se encuentren activos.
        """

        # En una actualización PUT/PATCH algunos valores
        # pueden provenir de la instancia existente.
        ruta = attrs.get(
            "ruta",
            getattr(self.instance, "ruta", None),
        )

        bus = attrs.get(
            "bus",
            getattr(self.instance, "bus", None),
        )

        if ruta and not ruta.activa:
            raise serializers.ValidationError(
                {
                    "ruta": (
                        "La ruta seleccionada "
                        "no se encuentra activa."
                    )
                }
            )

        if bus and not bus.activo:
            raise serializers.ValidationError(
                {
                    "bus": (
                        "El bus seleccionado "
                        "no se encuentra activo."
                    )
                }
            )

        return attrs
