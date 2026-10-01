"""
SEED DATA - POBLAMIENTO INICIAL DE LA BASE DE DATOS POSTGRESQL

Comando ejecutable mediante 'python manage.py seed' para cargar datos de Sistema de Buses Interurbanos.
"""

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import (
    CustomUser, Terminal, Ruta, Bus, Servicio, AsientoServicio
)


class Command(BaseCommand):
    help = "Pobla la base de datos de PostgreSQL con datos iniciales para el sistema de buses."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Limpiando datos antiguos de la base de datos..."))
        
        # 1. Limpieza de tablas principales
        Servicio.objects.all().delete()
        Bus.objects.all().delete()
        Ruta.objects.all().delete()
        Terminal.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Creando Usuarios con Roles..."))

        # 2. Creación de Usuarios (Pasajero y Administrador de Flota)
        pasajero, _ = CustomUser.objects.get_or_create(
            username="pasajero1",
            defaults={
                "email": "pasajero@correo.cl",
                "first_name": "Alexander",
                "last_name": "Lagos",
                "role": "PASAJERO"
            }
        )
        pasajero.set_password("pasajero123")
        pasajero.save()

        admin_flota, _ = CustomUser.objects.get_or_create(
            username="adminflota",
            defaults={
                "email": "admin@flota.cl",
                "first_name": "Carlos",
                "last_name": "Gestor",
                "role": "ADMIN_FLOTA"
            }
        )
        admin_flota.set_password("admin123")
        admin_flota.save()

        self.stdout.write(self.style.SUCCESS("Creando Terminales y Ciudades..."))

        # 3. Creación de Terminales
        term_santiago = Terminal.objects.create(nombre="Terminal Alameda", ciudad="Santiago")
        term_temuco = Terminal.objects.create(nombre="Terminal Rodoviario", ciudad="Temuco")
        term_concepcion = Terminal.objects.create(nombre="Terminal Collao", ciudad="Concepción")
        term_puerto_montt = Terminal.objects.create(nombre="Terminal Municipal", ciudad="Puerto Montt")

        self.stdout.write(self.style.SUCCESS("Creando Rutas Interurbanas..."))

        # 4. Creación de Rutas
        ruta_stgo_temuco = Ruta.objects.create(origen=term_santiago, destino=term_temuco, duracion_estimada_minutos=540)
        ruta_temuco_stgo = Ruta.objects.create(origen=term_temuco, destino=term_santiago, duracion_estimada_minutos=540)
        ruta_stgo_conce = Ruta.objects.create(origen=term_santiago, destino=term_concepcion, duracion_estimada_minutos=360)
        ruta_temuco_pmontt = Ruta.objects.create(origen=term_temuco, destino=term_puerto_montt, duracion_estimada_minutos=240)

        self.stdout.write(self.style.SUCCESS("Creando Flota de Buses..."))

        # 5. Creación de Buses
        bus_1 = Bus.objects.create(patente="KXYZ-88", marca_modelo="Marcopolo Paradiso 1800 DD", capacidad_asientos=20)
        bus_2 = Bus.objects.create(patente="BCDF-12", marca_modelo="Irizar i8 Premium", capacidad_asientos=20)

        self.stdout.write(self.style.SUCCESS("Creando Servicios e Itinerarios con Asientos..."))

        # 6. Creación de Servicios y Generación de Asientos
        ahora = timezone.now()
        
        servicios_datos = [
            (ruta_stgo_temuco, bus_1, ahora + timedelta(days=1, hours=8), ahora + timedelta(days=1, hours=17)),
            (ruta_temuco_stgo, bus_2, ahora + timedelta(days=1, hours=22), ahora + timedelta(days=2, hours=7)),
            (ruta_stgo_conce, bus_1, ahora + timedelta(days=2, hours=10), ahora + timedelta(days=2, hours=16)),
            (ruta_temuco_pmontt, bus_2, ahora + timedelta(days=3, hours=14), ahora + timedelta(days=3, hours=18)),
        ]

        for ruta, bus, salida, llegada in servicios_datos:
            servicio = Servicio.objects.create(
                ruta=ruta,
                bus=bus,
                fecha_hora_salida=salida,
                fecha_hora_llegada=llegada
            )

            # Genera 20 asientos para cada servicio (piso 1: Cama, piso 2: Semicama)
            for num in range(1, 21):
                tipo = 'CAMA' if num <= 6 else 'SEMICAMA'
                precio = 25000.00 if tipo == 'CAMA' else 18000.00

                AsientoServicio.objects.create(
                    servicio=servicio,
                    numero_asiento=num,
                    tipo_asiento=tipo,
                    precio=precio,
                    estado='DISPONIBLE'
                )

        self.stdout.write(self.style.SUCCESS("\n¡Base de Datos de PostgreSQL poblada exitosamente con datos de prueba!"))
        self.stdout.write(f"-> Usuario Pasajero: 'pasajero1' / Clave: 'pasajero123'")
        self.stdout.write(f"-> Usuario Admin Flota: 'adminflota' / Clave: 'admin123'")