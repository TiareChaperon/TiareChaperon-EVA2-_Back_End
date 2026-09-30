from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


# ==============================
# REGISTRO DE PASAJEROS
# ==============================

class RegistroPasajeroForm(UserCreationForm):
    """
    Formulario utilizado para registrar pasajeros.

    El rol no se solicita al usuario desde el formulario,
    ya que se asigna automáticamente como PASAJERO para
    evitar que una persona pueda registrarse a sí misma
    como Administrador de Flota.
    """

    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
        }

    # ==============================
    # GUARDAR PASAJERO
    # ==============================

    def save(self, commit=True):
        """
        Guarda el usuario asignando obligatoriamente
        el rol PASAJERO.
        """

        user = super().save(commit=False)

        user.role = "PASAJERO"

        if commit:
            user.save()

        return user
