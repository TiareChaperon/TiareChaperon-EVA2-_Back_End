import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from transporte.models import AsientoServicio


# ==============================
# VENTA
# ==============================

class Venta(models.Model):
    """
    Representa una transacción realizada por un pasajero.

    La venta se genera durante el checkout y mantiene
    un registro histórico independiente del carro.

    Su estado controla el ciclo de vida de la transacción:
    PENDIENTE -> PAGADO -> COMPLETADO
                         -> CANCELADO
    """

    ESTADO_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("PAGADO", "Pagado"),
        ("COMPLETADO", "Completado"),
        ("CANCELADO", "Cancelado"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ventas",
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default="PENDIENTE",
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    fecha_pago = models.DateTimeField(
        blank=True,
        null=True,
    )

    fecha_cancelacion = models.DateTimeField(
        blank=True,
        null=True,
    )

    # ==============================
    # VALIDACIÓN DE VENTA
    # ==============================

    def clean(self):
        """
        Verifica que solamente un usuario con rol
        PASAJERO pueda ser propietario de una venta.
        """

        if (
            self.usuario_id
            and self.usuario.role != "PASAJERO"
        ):
            raise ValidationError(
                "Solo un pasajero puede registrar una venta."
            )

    def __str__(self):
        return (
            f"Venta {self.id} - "
            f"{self.usuario.username} - "
            f"{self.get_estado_display()}"
        )


# ==============================
# DETALLE DE VENTA
# ==============================

class DetalleVenta(models.Model):
    """
    Representa cada pasaje incluido dentro de una venta.

    Conserva los datos del ocupante y el precio pagado
    como información histórica de la transacción.

    El precio se almacena deliberadamente aquí para que
    una modificación futura de la tarifa del servicio no
    altere una venta ya realizada.
    """

    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles",
    )

    asiento_servicio = models.ForeignKey(
        AsientoServicio,
        on_delete=models.PROTECT,
        related_name="detalles_venta",
    )

    nombre_ocupante = models.CharField(
        max_length=150,
    )

    documento_ocupante = models.CharField(
        max_length=30,
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "venta",
                    "asiento_servicio",
                ],
                name="unique_asiento_por_venta",
            )
        ]

    def __str__(self):
        return (
            f"Venta {self.venta_id} - "
            f"Asiento {self.asiento_servicio.asiento.numero} - "
            f"{self.nombre_ocupante}"
        )


# ==============================
# BOLETO
# ==============================

class Boleto(models.Model):
    """
    Representa el boleto emitido para un detalle de venta.

    Cada detalle genera como máximo un boleto mediante
    una relación OneToOne.

    El código UUID permite identificar cada boleto
    mediante un valor único y difícil de predecir.
    """

    detalle_venta = models.OneToOneField(
        DetalleVenta,
        on_delete=models.PROTECT,
        related_name="boleto",
    )

    codigo = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    fecha_emision = models.DateTimeField(
        auto_now_add=True,
    )

    utilizado = models.BooleanField(
        default=False,
    )

    fecha_utilizacion = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Boleto {self.codigo}"
