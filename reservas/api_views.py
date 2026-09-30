from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsPasajero

from .models import CarroPasajes, ItemCarro
from .serializers import (
    CarroPasajesSerializer,
    ItemCarroSerializer,
)


# ==========================================================
# API DEL CARRO DE PASAJES
# ==========================================================

class CarroPasajesView(APIView):
    """
    Permite al pasajero consultar su carro,
    agregar pasajes y eliminar pasajes.

    El carro pertenece siempre al usuario autenticado.
    """

    permission_classes = [IsPasajero]


    # ==============================
    # OBTENER CARRO
    # ==============================

    def obtener_carro(self, usuario):
        """
        Obtiene el carro persistente del pasajero.

        Si el usuario todavía no tiene un carro,
        se crea automáticamente.
        """

        carro, creado = CarroPasajes.objects.get_or_create(
            usuario=usuario,
            defaults={
                "estado": "ACTIVO",
            },
        )

        return carro


    # ==============================
    # GET - VER CARRO
    # ==============================

    def get(self, request):
        """
        Devuelve el carro del pasajero autenticado
        junto con todos sus pasajes.
        """

        carro = self.obtener_carro(
            request.user
        )

        serializer = CarroPasajesSerializer(
            carro
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


    # ==============================
    # POST - AGREGAR PASAJE
    # ==============================

    def post(self, request):
        """
        Agrega un asiento al carro del pasajero.

        Agregarlo al carro NO cambia el asiento
        a estado OCUPADO.
        """

        carro = self.obtener_carro(
            request.user
        )

        if carro.estado != "ACTIVO":
            return Response(
                {
                    "detail": (
                        "El carro no se encuentra activo."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ItemCarroSerializer(
            data=request.data
        )

        if serializer.is_valid():

            asiento_servicio = (
                serializer.validated_data[
                    "asiento_servicio"
                ]
            )

            # Evita agregar dos veces el mismo asiento
            # al carro del mismo pasajero.
            if ItemCarro.objects.filter(
                carro=carro,
                asiento_servicio=asiento_servicio,
            ).exists():

                return Response(
                    {
                        "detail": (
                            "Este asiento ya se encuentra "
                            "en tu carro."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            item = serializer.save(
                carro=carro
            )

            respuesta = ItemCarroSerializer(
                item
            )

            return Response(
                respuesta.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


    # ==============================
    # DELETE - ELIMINAR PASAJE
    # ==============================

    def delete(self, request):
        """
        Elimina un pasaje del carro del usuario.

        Se debe enviar el ID del item_carro
        que se desea eliminar.
        """

        item_id = request.data.get(
            "item_id"
        )

        if not item_id:
            return Response(
                {
                    "detail": (
                        "Debes indicar el item_id "
                        "que deseas eliminar."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        carro = self.obtener_carro(
            request.user
        )

        item = get_object_or_404(
            ItemCarro,
            id=item_id,
            carro=carro,
        )

        item.delete()

        return Response(
            {
                "detail": (
                    "Pasaje eliminado del carro correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )
