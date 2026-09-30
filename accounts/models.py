from django.contrib.auth.models import AbstractUser
from django.db import models


# ==============================
# USUARIO DEL SISTEMA
# ==============================

class User(AbstractUser):
    """
    Usuario personalizado del sistema de pasajes.

    Permite distinguir entre pasajeros y administradores
    de flota mediante el campo role.
    """

    ROLE_CHOICES = [
        ("PASAJERO", "Pasajero"),
        ("ADMIN_FLOTA", "Administrador de Flota"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="PASAJERO",
    )

    def __str__(self):
        return self.username
