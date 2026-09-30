from django import forms

from .models import (
    Asiento,
    AsientoServicio,
    Bus,
    Ciudad,
    Ruta,
    Servicio,
    Terminal,
)


# ==============================
# FORMULARIO DE CIUDAD
# ==============================

class CiudadForm(forms.ModelForm):
    """
    Formulario utilizado por el Administrador de Flota
    para crear y modificar ciudades.
    """

    class Meta:
        model = Ciudad

        fields = [
            "nombre",
        ]

        labels = {
            "nombre": "Nombre de la ciudad",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Temuco",
                }
            ),
        }


# ==============================
# FORMULARIO DE TERMINAL
# ==============================

class TerminalForm(forms.ModelForm):
    """
    Formulario utilizado por el Administrador de Flota
    para crear y modificar terminales.
    """

    class Meta:
        model = Terminal

        fields = [
            "nombre",
            "ciudad",
        ]

        labels = {
            "nombre": "Nombre del terminal",
            "ciudad": "Ciudad",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Terminal Rodoviario Temuco",
                }
            ),

            "ciudad": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


# ==============================
# FORMULARIO DE RUTA
# ==============================

class RutaForm(forms.ModelForm):
    """
    Formulario utilizado por el Administrador de Flota
    para crear y modificar rutas entre terminales.
    """

    class Meta:
        model = Ruta

        fields = [
            "terminal_origen",
            "terminal_destino",
            "activa",
        ]

        labels = {
            "terminal_origen": "Terminal de origen",
            "terminal_destino": "Terminal de destino",
            "activa": "Ruta activa",
        }

        widgets = {
            "terminal_origen": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "terminal_destino": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "activa": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


# ==============================
# FORMULARIO DE BUS
# ==============================

class BusForm(forms.ModelForm):
    """
    Formulario utilizado por el Administrador de Flota
    para crear y modificar buses.
    """

    class Meta:
        model = Bus

        fields = [
            "patente",
            "numero_bus",
            "activo",
        ]

        labels = {
            "patente": "Patente",
            "numero_bus": "Número del bus",
            "activo": "Bus activo",
        }

        widgets = {
            "patente": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: ABCD12",
                }
            ),

            "numero_bus": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: BUS-01",
                }
            ),

            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


# ==============================
# FORMULARIO DE ASIENTO
# ==============================

class AsientoForm(forms.ModelForm):
    """
    Formulario utilizado por el Administrador de Flota
    para crear y modificar los asientos físicos de un bus.
    """

    class Meta:
        model = Asiento

        fields = [
            "bus",
            "numero",
            "tipo",
        ]

        labels = {
            "bus": "Bus",
            "numero": "Número de asiento",
            "tipo": "Tipo de asiento",
        }

        widgets = {
            "bus": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "numero": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Ej: 1",
                }
            ),

            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }
# ==============================
# FORMULARIO DE SERVICIO
# ==============================

class ServicioForm(forms.ModelForm):
    """
    Formulario utilizado por el Administrador de Flota
    para crear y modificar servicios o itinerarios.

    Cada servicio relaciona una ruta, un bus y una
    fecha y hora específica de salida.
    """

    class Meta:
        model = Servicio

        fields = [
            "ruta",
            "bus",
            "fecha_hora_salida",
            "activo",
        ]

        labels = {
            "ruta": "Ruta",
            "bus": "Bus",
            "fecha_hora_salida": "Fecha y hora de salida",
            "activo": "Servicio activo",
        }

        widgets = {
            "ruta": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "bus": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "fecha_hora_salida": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),

            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        Configura el formato utilizado por el campo
        fecha_hora_salida al editar un servicio.
        """

        super().__init__(*args, **kwargs)

        self.fields["fecha_hora_salida"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]
# ==============================
# FORMULARIO DE ASIENTO SERVICIO
# ==============================

class AsientoServicioForm(forms.ModelForm):
    """
    Formulario utilizado por el Administrador de Flota
    para asociar un asiento físico a un servicio,
    indicando su tarifa y disponibilidad.
    """

    class Meta:
        model = AsientoServicio

        fields = [
            "servicio",
            "asiento",
            "tarifa",
            "estado",
        ]

        labels = {
            "servicio": "Servicio",
            "asiento": "Asiento",
            "tarifa": "Tarifa",
            "estado": "Estado",
        }

        widgets = {
            "servicio": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "asiento": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "tarifa": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "1",
                    "placeholder": "Ej: 30000",
                }
            ),

            "estado": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }
