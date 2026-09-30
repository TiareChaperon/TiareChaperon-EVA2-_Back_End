Pasajes Bus — EVA2

Sistema web de venta y gestión de pasajes de buses interurbanos desarrollado con Django.

#Descripción

El proyecto permite gestionar servicios de transporte y realizar el proceso de compra y validación de pasajes.

#Funcionalidades

- Registro e inicio de sesión de usuarios.
- Gestión de ciudades y terminales.
- Gestión de rutas.
- Gestión de buses y asientos.
- Creación y administración de servicios de viaje.
- Búsqueda de pasajes por origen, destino y fecha.
- Selección de asientos.
- Compra de pasajes.
- Consulta de boletos.
- Validación de boletos.
- Control de permisos según el tipo de usuario.
- API REST.
- Autenticación mediante JWT.

Roles de usuario

Pasajero

Puede:

- Registrarse e iniciar sesión.
- Buscar viajes.
- Seleccionar asientos.
- Comprar pasajes.
- Consultar sus boletos.

Administrador de flota

Puede gestionar los elementos relacionados con la operación de los buses y validar boletos.

Tecnologías utilizadas

- Python
- Django
- Django REST Framework
- PostgreSQL
- HTML
- CSS
- Git
- GitHub

Estructura principal

PasajesBus/
├── accounts/
├── reservas/
├── transporte/
├── ventas/
├── templates/
├── PasajesBus/
├── cargar_servicios.py
├── manage.py
└── .gitignore

Base de datos
El proyecto utiliza PostgreSQL como sistema de gestión de base de datos.
Las credenciales de conexión se manejan mediante variables de entorno y no se almacenan en el repositorio.
Autenticación
El sistema utiliza autenticación web para los usuarios y JWT para los endpoints de la API.
