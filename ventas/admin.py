from django.contrib import admin

from .models import (
    Venta,
    DetalleVenta,
    Boleto,
)


admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Boleto)
