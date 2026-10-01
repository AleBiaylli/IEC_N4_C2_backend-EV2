"""
=============================================================================
SCRIPT DE POBLAMIENTO NACIONAL DE DATOS - BUSES INTERURBANOS (ZONA NORTE, ZONA CENTRO, ZONA SUR, ZONA AUSTRAL)
=============================================================================
"""

import os
import django
from decimal import Decimal

# Configuración del entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IEC_N4_C2_backend.settings')
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
from api.models import Terminal, Ruta, Bus, Servicio, AsientoServicio

def cargar_todos_los_destinos_chile():
    print("Iniciando poblamiento de terminales (incluyendo Toltén)...")

    # 1. LISTADO DE CIUDADES CON TERMINALES EN CHILE
    ciudades_chile = [
        # Zona Norte
        "Arica", "Iquique", "Calama", "Antofagasta", "Copiapó", "La Serena", "Coquimbo",
        # Zona Centro
        "Valparaíso", "Viña del Mar", "Santiago", "Rancagua", "Talca", "Curicó", "Chillán", "Concepción", "Los Ángeles",
        # Zona Sur & La Araucanía
        "Temuco", "Toltén", "Gorbea", "Pitrufquén", "Pucón", "Villarrica", "Valdivia", "Osorno", "Puerto Montt", "Ancud", "Castro",
        # Zona Austral
        "Coyhaique", "Punta Arenas"
    ]

    terminales_objs = {}
    for ciudad in ciudades_chile:
        term = Terminal.objects.filter(ciudad__iexact=ciudad).first()
        if not term:
            try:
                term = Terminal.objects.create(
                    ciudad=ciudad,
                    nombre=f"Terminal Rodoviario {ciudad}"
                )
            except Exception:
                term = Terminal.objects.create(ciudad=ciudad)
        
        terminales_objs[ciudad] = term
        print(f" Terminal registrado: {ciudad}")

    # 2. FLOTA DE BUSES
    buses_data = [
        ("KPB-102", 40),
        ("RST-884", 42),
        ("HH-9012", 38),
        ("BB-3344", 44),
        ("FL-5020", 40),
        ("CX-7711", 42)
    ]
    
    buses_objs = []
    for patente, capacidad in buses_data:
        bus = Bus.objects.filter(patente=patente).first()
        if not bus:
            bus = Bus.objects.create(patente=patente, capacidad_asientos=capacidad)
        buses_objs.append(bus)
        print(f" Bus registrado: {patente} ({capacidad} asientos)")

    # 3. RUTAS CON DURACIÓN ESTIMADA EN MINUTOS
    rutas_red = [
        ("Santiago", "Temuco", 480),
        ("Santiago", "Toltén", 540),
        ("Temuco", "Toltén", 90),
        ("Toltén", "Temuco", 90),
        ("Santiago", "Concepción", 360),
        ("Santiago", "Valparaíso", 120),
        ("Temuco", "Puerto Montt", 240),
        ("Temuco", "Valdivia", 180),
        ("Concepción", "Valdivia", 300),
        ("Puerto Montt", "Castro", 210)
    ]

    rutas_objs = []
    for origen_c, destino_c, duracion_min in rutas_red:
        if origen_c in terminales_objs and destino_c in terminales_objs:
            ruta, _ = Ruta.objects.get_or_create(
                origen=terminales_objs[origen_c],
                destino=terminales_objs[destino_c],
                defaults={'duracion_estimada_minutos': duracion_min}
            )
            rutas_objs.append(ruta)

    # 4. ITINERARIOS Y ASIENTOS (CAMA / SEMI CAMA)
    ahora = timezone.now()
    horas_salida = [7, 11, 15, 20, 22]

    print("\nGenerando itinerarios con Toltén y red nacional...")
    for i, ruta in enumerate(rutas_objs):
        bus_asignado = buses_objs[i % len(buses_objs)]
        
        for dia in range(0, 5):
            fecha_base = ahora + timedelta(days=dia)
            for hora in horas_salida:
                fecha_salida = fecha_base.replace(hour=hora, minute=0, second=0, microsecond=0)

                # Se crea el servicio pasando solo la fecha de salida aware
                servicio = Servicio.objects.filter(
                    ruta=ruta,
                    bus=bus_asignado,
                    fecha_hora_salida=fecha_salida
                ).first()

                if not servicio:
                    try:
                        servicio = Servicio.objects.create(
                            ruta=ruta,
                            bus=bus_asignado,
                            fecha_hora_salida=fecha_salida
                        )
                    except Exception:
                        duracion_min = getattr(ruta, 'duracion_estimada_minutos', 480)
                        fecha_llegada = fecha_salida + timedelta(minutes=duracion_min)
                        servicio = Servicio.objects.create(
                            ruta=ruta,
                            bus=bus_asignado,
                            fecha_hora_salida=fecha_salida,
                            fecha_hora_llegada=fecha_llegada
                        )

                    # Creación automática de la grilla de asientos
                    cap = getattr(bus_asignado, 'capacidad_asientos', 40)
                    for n in range(1, cap + 1):
                        tipo = 'CAMA' if n <= 12 else 'SEMI_CAMA'
                        precio = Decimal('18000.00') if tipo == 'CAMA' else Decimal('12000.00')

                        AsientoServicio.objects.create(
                            servicio=servicio,
                            numero_asiento=n,
                            tipo_asiento=tipo,
                            precio=precio,
                            estado='DISPONIBLE'
                        )

    print("\n ¡Poblamiento de datos completado 100% con éxito!")

if __name__ == '__main__':
    cargar_todos_los_destinos_chile()