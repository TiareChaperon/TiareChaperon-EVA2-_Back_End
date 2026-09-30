from django.urls import path

from .api_views import CarroPasajesView


urlpatterns = [
    path(
        "carro-pasajes/",
        CarroPasajesView.as_view(),
        name="carro_pasajes_api",
    ),
]
