from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Terminal,
    Ruta,
    Bus,
    Servicio,
    AsientoServicio,
    CarroPasajes,
    ItemCarro,
    Venta,
    Boleto,
)

# Configuración del usuario personalizado en el Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Rol', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')

# Registro de entidades base
@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ciudad')
    search_fields = ('nombre', 'ciudad')

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ('id', 'origen', 'destino', 'duracion_estimada_minutos')

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('id', 'patente', 'marca_modelo', 'capacidad_asientos')
    search_fields = ('patente', 'marca_modelo')

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'ruta', 'bus', 'fecha_hora_salida', 'fecha_hora_llegada')
    list_filter = ('fecha_hora_salida',)

@admin.register(AsientoServicio)
class AsientoServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'servicio', 'numero_asiento', 'tipo_asiento', 'precio', 'estado')
    list_filter = ('tipo_asiento', 'estado', 'servicio')

# Registro de Carro y Transacciones
@admin.register(CarroPasajes)
class CarroPasajesAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_creacion')

@admin.register(ItemCarro)
class ItemCarroAdmin(admin.ModelAdmin):
    list_display = ('id', 'carro', 'asiento_servicio', 'pasajero_nombre', 'pasajero_rut_pasaporte')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('codigo_uuid', 'usuario', 'monto_total', 'estado', 'fecha_venta')
    list_filter = ('estado', 'fecha_venta')

@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ('codigo_boleto', 'venta', 'pasajero_nombre', 'pasajero_rut_pasaporte', 'precio_historico')