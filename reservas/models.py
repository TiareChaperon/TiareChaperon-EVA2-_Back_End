from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from transporte.models import AsientoServicio


# ==============================
# CARRO DE PASAJES
# ==============================

class CarroPasajes(models.Model):
    """
    Representa el carro persistente de un pasajero.

    El carro se almacena en PostgreSQL mediante una relación
    OneToOne con el usuario, permitiendo conservar sus ítems
    aunque el pasajero cierre sesión o cambie de dispositivo.

    El estado permite distinguir un carro disponible para
    agregar/quitar pasajes de uno que ya fue liquidado.
    """

    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("LIQUIDADO", "Liquidado"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carro_pasajes",
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default="ACTIVO",
    )

    creado = models.DateTimeField(
        auto_now_add=True,
    )

    actualizado = models.DateTimeField(
        auto_now=True,
    )

    # ==============================
    # VALIDACIÓN DEL CARRO
    # ==============================

    def clean(self):
        """
        Verifica que solamente un usuario con rol
        PASAJERO pueda ser propietario de un carro.
        """

        if (
            self.usuario_id
            and self.usuario.role != "PASAJERO"
        ):
            raise ValidationError(
                "Solo un pasajero puede tener un carro de pasajes."
            )

    def __str__(self):
        return (
            f"Carro de {self.usuario.username} - "
            f"{self.get_estado_display()}"
        )


# ==============================
# ÍTEM DEL CARRO
# ==============================

class ItemCarro(models.Model):
    """
    Representa un asiento seleccionado por el pasajero.

    Almacena los datos del ocupante solicitados por el
    negocio: nombre completo y RUT/Pasaporte.

    Agregar un asiento al carro NO descuenta disponibilidad.
    El asiento será validado nuevamente de forma atómica
    cuando la venta sea procesada como PAGADA.
    """

    carro = models.ForeignKey(
        CarroPasajes,
        on_delete=models.CASCADE,
        related_name="items",
    )

    asiento_servicio = models.ForeignKey(
        AsientoServicio,
        on_delete=models.PROTECT,
        related_name="items_carro",
    )

    nombre_ocupante = models.CharField(
        max_length=150,
    )

    documento_ocupante = models.CharField(
        max_length=30,
    )

    agregado = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "carro",
                    "asiento_servicio",
                ],
                name="unique_asiento_en_carro",
            )
        ]

    # ==============================
    # VALIDACIÓN DEL ÍTEM
    # ==============================

    def clean(self):
        """
        Valida que:

        1. El carro se encuentre ACTIVO.
        2. El asiento todavía no esté marcado como OCUPADO.

        Estas validaciones no reemplazan la comprobación
        atómica realizada posteriormente durante el pago.
        """

        if (
            self.carro_id
            and self.carro.estado != "ACTIVO"
        ):
            raise ValidationError(
                "No se pueden agregar pasajes a un carro liquidado."
            )

        if (
            self.asiento_servicio_id
            and self.asiento_servicio.estado == "OCUPADO"
        ):
            raise ValidationError(
                "El asiento seleccionado ya se encuentra ocupado."
            )

    def __str__(self):
        return (
            f"{self.carro.usuario.username} - "
            f"Asiento {self.asiento_servicio.asiento.numero} - "
            f"{self.nombre_ocupante}"
        )
