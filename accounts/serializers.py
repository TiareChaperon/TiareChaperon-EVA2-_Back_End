from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# ==============================
# TOKEN JWT PERSONALIZADO
# ==============================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza el token JWT para incluir información
    adicional del usuario autenticado.

    Se agrega el rol para que la API pueda identificar
    si corresponde a un PASAJERO o ADMIN_FLOTA.
    """

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        # Claims personalizados del JWT.
        token["username"] = user.username
        token["role"] = user.role

        return token
