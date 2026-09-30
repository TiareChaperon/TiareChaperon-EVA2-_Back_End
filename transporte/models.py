from django.core.exceptions import ValidationError
from django.db import models


# ==============================
# CIUDAD
# ==============================

class Ciudad(models.Model):
    """
    Representa una ciudad disponible dentro del sistema
    de transporte interurbano.
    """

    nombre = models.CharField(
        max_length=100,
        unique=True,
    )

    def __str__(self):
        return self.nombre


# ==============================
# TERMINAL
# ==============================

class Terminal(models.Model):
    """
    Representa un terminal de buses.

    Cada terminal pertenece a una ciudad, evitando
    repetir información y manteniendo el modelo
    normalizado en 3FN.
    """

    nombre = models.CharField(
        max_length=150,
    )

    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.PROTECT,
        related_name="terminales",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "ciudad"],
                name="unique_terminal_ciudad",
            )
        ]

    def __str__(self):
        return f"{self.nombre} - {self.ciudad.nombre}"


# ==============================
# RUTA
# ==============================

class Ruta(models.Model):
    """
    Representa el recorrido entre un terminal de origen
    y un terminal de destino.
    """

    terminal_origen = models.ForeignKey(
        Terminal,
        on_delete=models.PROTECT,
        related_name="rutas_origen",
    )

    terminal_destino = models.ForeignKey(
        Terminal,
        on_delete=models.PROTECT,
        related_name="rutas_destino",
    )

    activa = models.BooleanField(
        default=True,
    )

    class Meta:
      constraints = [
        # Evita duplicar una misma ruta.
        models.UniqueConstraint(
            fields=[
                "terminal_origen",
                "terminal_destino",
            ],
            name="unique_ruta_origen_destino",
        ),

        # Impide que origen y destino sean el mismo terminal.
        models.CheckConstraint(
            condition=~models.Q(
                terminal_origen=models.F("terminal_destino")
            ),
            name="ruta_origen_destino_diferentes",
        ),
    ]

    # ==============================
    # VALIDACIÓN DE RUTA
    # ==============================

    def clean(self):
        """
        Impide crear una ruta cuyo terminal de origen
        sea igual al terminal de destino.
        """

        if (
            self.terminal_origen_id
            and self.terminal_destino_id
            and self.terminal_origen_id == self.terminal_destino_id
        ):
            raise ValidationError(
                "El terminal de origen y destino no pueden ser iguales."
            )

    def __str__(self):
        return (
            f"{self.terminal_origen} → "
            f"{self.terminal_destino}"
        )


# ==============================
# BUS
# ==============================

class Bus(models.Model):
    """
    Representa un bus físico perteneciente a la flota.

    Los asientos se almacenan en una entidad separada
    para evitar datos repetidos y mantener la 3FN.
    """

    patente = models.CharField(
        max_length=10,
        unique=True,
    )

    numero_bus = models.CharField(
        max_length=20,
        unique=True,
    )

    activo = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"Bus {self.numero_bus} - {self.patente}"


# ==============================
# ASIENTO
# ==============================

class Asiento(models.Model):
    """
    Representa un asiento físico perteneciente a un bus.

    Cada asiento posee un tipo definido mediante CHOICES:
    Semicama o Cama.
    """

    TIPO_CHOICES = [
        ("SEMICAMA", "Semicama"),
        ("CAMA", "Cama"),
    ]

    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name="asientos",
    )

    numero = models.PositiveIntegerField()

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bus", "numero"],
                name="unique_asiento_bus",
            )
        ]

        ordering = [
            "bus",
            "numero",
        ]

    def __str__(self):
        return (
            f"Bus {self.bus.numero_bus} - "
            f"Asiento {self.numero} "
            f"({self.get_tipo_display()})"
        )


# ==============================
# SERVICIO / ITINERARIO
# ==============================

class Servicio(models.Model):
    """
    Representa un viaje específico.

    Relaciona una ruta con un bus determinado y
    establece la fecha y hora de salida.
    """

    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.PROTECT,
        related_name="servicios",
    )

    bus = models.ForeignKey(
        Bus,
        on_delete=models.PROTECT,
        related_name="servicios",
    )

    fecha_hora_salida = models.DateTimeField()

    activo = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return (
            f"{self.ruta} - "
            f"{self.fecha_hora_salida:%d/%m/%Y %H:%M}"
        )


# ==============================
# ASIENTO POR SERVICIO
# ==============================

class AsientoServicio(models.Model):
    """
    Representa un asiento dentro de un servicio específico.

    El asiento físico pertenece al bus, mientras que
    la tarifa y disponibilidad corresponden al viaje
    específico.
    """

    ESTADO_CHOICES = [
        ("DISPONIBLE", "Disponible"),
        ("OCUPADO", "Ocupado"),
    ]

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name="asientos_servicio",
    )

    asiento = models.ForeignKey(
        Asiento,
        on_delete=models.PROTECT,
        related_name="servicios_asignados",
    )

    tarifa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default="DISPONIBLE",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "servicio",
                    "asiento",
                ],
                name="unique_asiento_servicio",
            )
        ]

        ordering = [
            "asiento__numero",
        ]

    # ==============================
    # VALIDACIÓN DE ASIENTO
    # ==============================

    def clean(self):
        """
        Verifica que el asiento seleccionado pertenezca
        al mismo bus asignado al servicio.
        """

        if (
            self.servicio_id
            and self.asiento_id
            and self.servicio.bus_id != self.asiento.bus_id
        ):
            raise ValidationError(
                "El asiento no pertenece al bus asignado a este servicio."
            )

    def __str__(self):
        return (
            f"{self.servicio} - "
            f"Asiento {self.asiento.numero} - "
            f"{self.get_estado_display()}"
        )
