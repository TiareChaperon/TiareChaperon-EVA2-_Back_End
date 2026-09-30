from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


# ==========================================================
# CONTROL DE ACCESO A DOCUMENTACIÓN API
# ==========================================================

def es_admin_flota(user):
    return (
        user.is_authenticated
        and getattr(user, "role", None) == "ADMIN_FLOTA"
    )


@login_required(login_url="/login/")
def schema_protegido(request):

    if not es_admin_flota(request.user):
        return render(
            request,
            "403.html",
            status=403,
        )

    vista_schema = SpectacularAPIView.as_view()

    return vista_schema(request)


@login_required(login_url="/login/")
def swagger_protegido(request):

    if not es_admin_flota(request.user):
        return render(
            request,
            "403.html",
            status=403,
        )

    vista_swagger = SpectacularSwaggerView.as_view(
        url_name="schema"
    )

    return vista_swagger(request)


# ==========================================================
# URLS DEL PROYECTO
# ==========================================================

urlpatterns = [

    # ======================================================
    # PÁGINAS WEB
    # ======================================================
    path("admin/", admin.site.urls),

    path(
        "",
        include("accounts.urls"),
    ),

    path(
        "transporte/",
        include("transporte.urls"),
    ),

    path(
        "reservas/",
        include("reservas.urls"),
    ),

    path(
        "ventas/",
        include("ventas.urls"),
    ),


    # ======================================================
    # AUTENTICACIÓN API
    # ======================================================

    path(
        "api/auth/",
        include("accounts.api_urls"),
    ),


    # ======================================================
    # API
    # ======================================================

    path(
        "api/",
        include("transporte.api_urls"),
    ),

    path(
        "api/",
        include("reservas.api_urls"),
    ),

    path(
        "api/",
        include("ventas.api_urls"),
    ),


    # ======================================================
    # DOCUMENTACIÓN OPENAPI / SWAGGER
    # SOLO ADMINISTRADOR DE FLOTA
    # ======================================================

    path(
        "api/schema/",
        schema_protegido,
        name="schema",
    ),

    path(
        "api/docs/",
        swagger_protegido,
        name="swagger-ui",
    ),

]
