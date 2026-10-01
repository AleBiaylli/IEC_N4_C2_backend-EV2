import os
import django

# Configura el módulo de settings de tu proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IEC_N4_C2_backend.settings')
django.setup()

from django.db import connection

print("Limpiando esquema público de PostgreSQL...")
with connection.cursor() as cursor:
    cursor.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
print("¡Esquema de PostgreSQL limpiado con éxito!")
