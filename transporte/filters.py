import django_filters

from .models import Servicio


# ==============================
# FILTROS DE SERVICIOS
# ==============================

class ServicioFilter(django_filters.FilterSet):
    """
    Permite buscar servicios disponibles utilizando
    ciudad de origen, ciudad de destino y fecha.

    Los filtros recorren las relaciones normalizadas
    entre Servicio, Ruta, Terminal y Ciudad.
    """

    origen = django_filters.CharFilter(
        field_name="ruta__terminal_origen__ciudad__nombre",
        lookup_expr="icontains",
    )

    destino = django_filters.CharFilter(
        field_name="ruta__terminal_destino__ciudad__nombre",
        lookup_expr="icontains",
    )

    fecha = django_filters.DateFilter(
        field_name="fecha_hora_salida",
        lookup_expr="date",
    )

    class Meta:
        model = Servicio

        fields = [
            "origen",
            "destino",
            "fecha",
        ]
