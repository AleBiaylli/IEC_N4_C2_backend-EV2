"""
Módulo encargado de transformar las instancias de los modelos en JSON y 
viceversa, incluyendo validación de datos para la gestión del carro de 
pasajes y transacciones de checkout.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    CustomUser, Terminal, Ruta, Bus, Servicio, 
    AsientoServicio, CarroPasajes, ItemCarro, Venta, Boleto
)


# ---------------------------------------------------------------------------
# 1. AUTENTICACIÓN Y ROLES (JWT CLAIMS)
# ---------------------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador JWT personalizado para incorporar el rol del usuario 
    (PASAJERO / ADMIN_FLOTA) directamente en el payload del token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Inclusión explícita de claims según pauta técnica
        token['role'] = getattr(user, 'role', 'PASAJERO')
        token['username'] = user.username
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Retorna los datos básicos del usuario en la respuesta HTTP del login
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['role'] = getattr(self.user, 'role', 'PASAJERO')
        return data


# ---------------------------------------------------------------------------
# 2. CATÁLOGO BASE Y FLOTA DE BUSES
# ---------------------------------------------------------------------------
class CustomUserSerializer(serializers.ModelSerializer):
    """Serializador para el modelo de usuario con rol."""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class TerminalSerializer(serializers.ModelSerializer):
    """Serializador para ciudades y terminales interurbanos."""
    class Meta:
        model = Terminal
        fields = '__all__'


class RutaSerializer(serializers.ModelSerializer):
    """Serializador de rutas con detalle anidado de terminal origen y destino."""
    origen_detalle = TerminalSerializer(source='origen', read_only=True)
    destino_detalle = TerminalSerializer(source='destino', read_only=True)

    class Meta:
        model = Ruta
        fields = ['id', 'origen', 'destino', 'origen_detalle', 'destino_detalle', 'duracion_estimada_minutos']


class BusSerializer(serializers.ModelSerializer):
    """Serializador para la información de buses de la flota."""
    class Meta:
        model = Bus
        fields = '__all__'


class AsientoServicioSerializer(serializers.ModelSerializer):
    """Serializador para los asientos asociados a un itinerario específico."""
    class Meta:
        model = AsientoServicio
        fields = ['id', 'numero_asiento', 'tipo_asiento', 'precio', 'estado']


class ServicioSerializer(serializers.ModelSerializer):
    """
    Serializador de itinerarios/servicios con relaciones anidadas de 
    ruta y bus.
    """
    ruta_detalle = RutaSerializer(source='ruta', read_only=True)
    bus_detalle = BusSerializer(source='bus', read_only=True)

    class Meta:
        model = Servicio
        fields = ['id', 'ruta', 'bus', 'fecha_hora_salida', 'fecha_hora_llegada', 'ruta_detalle', 'bus_detalle']


# ---------------------------------------------------------------------------
# 3. CARRO DE COMPRAS PERSISTENTE
# ---------------------------------------------------------------------------
class ItemCarroSerializer(serializers.ModelSerializer):
    """
    Serializador para cada asiento registrado en el carro de un pasajero.
    Informa el detalle del asiento y los datos del ocupante (Nombre/RUT).
    """
    asiento_detalle = AsientoServicioSerializer(source='asiento_servicio', read_only=True)

    class Meta:
        model = ItemCarro
        fields = ['id', 'asiento_servicio', 'asiento_detalle', 'pasajero_nombre', 'pasajero_rut_pasaporte']

    def validate_asiento_servicio(self, value):
        """Valida que el asiento no haya sido tomado previamente por otro usuario."""
        if value.estado == 'OCUPADO':
            raise serializers.ValidationError("El asiento seleccionado ya está ocupado.")
        return value


class CarroPasajesSerializer(serializers.ModelSerializer):
    """
    Serializador para el carro activo del usuario (Persistente 1:1 en DB).
    """
    items = ItemCarroSerializer(many=True, read_only=True)

    class Meta:
        model = CarroPasajes
        fields = ['id', 'usuario', 'fecha_creacion', 'items']


# ---------------------------------------------------------------------------
# 4. TRANSACCIONES Y EMISIÓN DE BOLETOS
# ---------------------------------------------------------------------------
class BoletoSerializer(serializers.ModelSerializer):
    """Serializador para los boletos de viaje emitidos tras la confirmación de pago."""
    class Meta:
        model = Boleto
        fields = ['id', 'codigo_boleto', 'asiento_servicio', 'pasajero_nombre', 'pasajero_rut_pasaporte', 'precio_historico']


class VentaSerializer(serializers.ModelSerializer):
    """Serializador para el registro histórico de la transacción de compra."""
    boletos = BoletoSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'codigo_uuid', 'usuario', 'monto_total', 'estado', 'fecha_venta', 'boletos']