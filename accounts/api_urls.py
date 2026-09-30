from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .api_views import CustomTokenObtainPairView


# ==============================
# RUTAS DE AUTENTICACIÓN JWT
# ==============================

urlpatterns = [

    # Login JWT: genera access + refresh.
    path(
        "login/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    # Permite obtener un nuevo access utilizando
    # un refresh token válido.
    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

]
