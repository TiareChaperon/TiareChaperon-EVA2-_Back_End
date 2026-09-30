from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import RegistroPasajeroForm


# ==============================
# PÁGINA DE INICIO
# ==============================

def inicio(request):
    """
    Muestra la página principal del sistema.

    Posteriormente esta vista contendrá la búsqueda
    pública de servicios de buses.
    """

    return render(
        request,
        "accounts/inicio.html",
    )


# ==============================
# REGISTRO DE PASAJEROS
# ==============================

def registro_pasajero(request):
    """
    Permite registrar nuevos pasajeros mediante
    una vista HTML propia.

    El rol PASAJERO se asigna automáticamente desde
    el formulario y no puede ser elegido por el usuario.
    """

    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":

        form = RegistroPasajeroForm(request.POST)

        if form.is_valid():

            usuario = form.save()

            # Inicia sesión automáticamente
            # después del registro.
            login(request, usuario)

            return redirect("inicio")

    else:

        form = RegistroPasajeroForm()

    return render(
        request,
        "accounts/registro.html",
        {
            "form": form,
        },
    )


# ==============================
# INICIAR SESIÓN
# ==============================

def iniciar_sesion(request):
    """
    Autentica al usuario utilizando su nombre de
    usuario y contraseña.

    Si las credenciales son correctas, Django crea
    la sesión correspondiente.
    """

    if request.user.is_authenticated:
        return redirect("inicio")

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=username,
            password=password,
        )

        if usuario is not None:

            login(request, usuario)

            return redirect("inicio")

        error = "Usuario o contraseña incorrectos."

    return render(
        request,
        "accounts/login.html",
        {
            "error": error,
        },
    )


# ==============================
# CERRAR SESIÓN
# ==============================

def cerrar_sesion(request):
    """
    Finaliza la sesión del usuario actual.

    Los datos almacenados en PostgreSQL, incluido
    posteriormente el carro de pasajes, no se eliminan.
    """

    if request.method == "POST":
        logout(request)

    return redirect("inicio")
