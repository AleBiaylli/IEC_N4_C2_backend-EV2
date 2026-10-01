"""
SCRIPT DE CREACIÓN DE USUARIOS CLIENTES REALISTAS

Crea cuentas de usuario con roles de CLIENTE / PASAJERO utilizando nombres
e emails institucionales para las pruebas del sistema de pasajes.
"""

import os
import django

# Configuración del entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IEC_N4_C2_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def crear_clientes():
    print("Iniciando creación de cuentas de clientes reales...")

    # Lista de clientes con credenciales formales
    clientes = [
        {
            'username': 'alexander.lagos',
            'email': 'alexander.lagos@inacapmail.cl',
            'first_name': 'Alexander',
            'last_name': 'Lagos',
            'password': 'Biaylli20070!',
            'role': 'PASAJERO'
        },
        {
            'username': 'carlos.mendoza',
            'email': 'carlos.mendoza@empresa.cl',
            'first_name': 'Carlos',
            'last_name': 'Mendoza',
            'password': 'ClientePass2026!',
            'role': 'PASAJERO'
        },
        {
            'username': 'valentina.silva',
            'email': 'v.silva@transporte.cl',
            'first_name': 'Valentina',
            'last_name': 'Silva',
            'password': 'ClientePass2026!',
            'role': 'PASAJERO'
        }
    ]

    for data_user in clientes:
        username = data_user['username']
        email = data_user['email']
        password = data_user['password']
        
        user = User.objects.filter(username=username).first()
        if not user:
            # Creación usando el CustomUser configurado en tu proyecto
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=data_user['first_name'],
                last_name=data_user['last_name']
            )
            # Asignar rol de pasajero/cliente si el modelo custom posee el atributo
            if hasattr(user, 'role'):
                user.role = data_user['role']
                user.save()
            print(f" Usuario creado: {username} | Email: {email}")
        else:
            # Si el usuario ya existe, actualizamos su contraseña para garantizar el acceso
            user.set_password(password)
            user.save()
            print(f" Usuario actualizado: {username} | Email: {email}")

    print("\n ¡Usuarios registrados con éxito!")

if __name__ == '__main__':
    crear_clientes()