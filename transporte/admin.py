from django.contrib import admin

from .models import (
    Ciudad,
    Terminal,
    Ruta,
    Bus,
    Asiento,
    Servicio,
    AsientoServicio,
)


admin.site.register(Ciudad)
admin.site.register(Terminal)
admin.site.register(Ruta)
admin.site.register(Bus)
admin.site.register(Asiento)
admin.site.register(Servicio)
admin.site.register(AsientoServicio)
