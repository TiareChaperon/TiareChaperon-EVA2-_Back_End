from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer


# ==============================
# LOGIN JWT
# ==============================

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint encargado de autenticar al usuario y
    entregar los tokens access y refresh.

    Utiliza un serializer personalizado para incluir
    el rol del usuario dentro del payload JWT.
    """

    serializer_class = CustomTokenObtainPairSerializer
