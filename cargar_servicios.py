import os
import django
from datetime import datetime, timedelta


# ==============================
# CONFIGURAR DJANGO
# ==============================

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "PasajesBus.settings"
)

django.setup()


from transporte.models import (
    Servicio,
    AsientoServicio,
    Bus,
    Ruta,
)


# ==============================
# CONFIGURACIÓN DE SERVICIOS
# ==============================

CONFIG = [

    {
        "bus": "BUS-01",
        "ruta_id": 1,   # Temuco → Santiago
        "horarios": [
            "08:00",
            "22:00"
        ],
        "tarifa_base": 35000
    },


    {
        "bus": "BUS-02",
        "ruta_id": 2,   # Temuco → Valdivia
        "horarios": [
            "09:00",
            "17:00"
        ],
        "tarifa_base": 18000
    },


    {
        "bus": "BUS-03",
        "ruta_id": 4,   # Temuco → Concepción
        "horarios": [
            "10:00",
            "18:00"
        ],
        "tarifa_base": 22000
    },


    {
        "bus": "BUS-04",
        "ruta_id": 3,   # Temuco → Puerto Montt
        "horarios": [
            "12:00",
            "20:00"
        ],
        "tarifa_base": 30000
    },


    {
        "bus": "BUS-05",
        "ruta_id": 6,   # Santiago → Chillán
        "horarios": [
            "08:00",
            "14:00",
            "22:00"
        ],
        "tarifa_base": 20000
    },

]


# ==============================
# FECHAS
# ==============================

FECHA_INICIO = datetime(
    2026,
    9,
    1
)

DIAS = 30


# ==============================
# CONTADORES
# ==============================

servicios_creados = 0
asientos_creados = 0



# ==============================
# CREACIÓN
# ==============================


for dia in range(DIAS):

    fecha = FECHA_INICIO + timedelta(days=dia)


    for item in CONFIG:


        bus = Bus.objects.get(
            numero_bus=item["bus"]
        )


        ruta = Ruta.objects.get(
            id=item["ruta_id"]
        )


        for hora in item["horarios"]:


            hora_salida = datetime.strptime(
                hora,
                "%H:%M"
            ).time()


            fecha_hora = datetime.combine(
                fecha.date(),
                hora_salida
            )


            servicio, creado = Servicio.objects.get_or_create(
                ruta=ruta,
                bus=bus,
                fecha_hora_salida=fecha_hora,
                defaults={
                    "activo": True
                }
            )


            if creado:

                servicios_creados += 1


            # ==============================
            # CREAR ASIENTOS DEL SERVICIO
            # ==============================


            for asiento in bus.asientos.all():


                if asiento.tipo == "CAMA":

                    tarifa = (
                        item["tarifa_base"]
                        + 10000
                    )

                else:

                    tarifa = item["tarifa_base"]



                _, creado_asiento = AsientoServicio.objects.get_or_create(

                    servicio=servicio,

                    asiento=asiento,

                    defaults={

                        "tarifa": tarifa,

                        "estado": "DISPONIBLE"

                    }

                )


                if creado_asiento:

                    asientos_creados += 1



print("==============================")
print("CARGA TERMINADA")
print("==============================")
print(
    f"Servicios creados: {servicios_creados}"
)
print(
    f"Asientos creados: {asientos_creados}"
)
print("==============================")
