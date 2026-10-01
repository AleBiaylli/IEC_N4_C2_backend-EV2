import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# ---------------------------------------------------------------------
# 1. USUARIO PERSONALIZADO CON ROLES
# ---------------------------------------------------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('PASAJERO', 'Pasajero'),
        ('ADMIN_FLOTA', 'Administrador de Flota'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PASAJERO')


# ---------------------------------------------------------------------
# 2. INFRAESTRUCTURA Y RUTAS
# ---------------------------------------------------------------------
class Terminal(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.ciudad})"


class Ruta(models.Model):
    origen = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name='rutas_origen')
    destino = models.ForeignKey(Terminal, on_delete=models.CASCADE, related_name='rutas_destino')
    duracion_estimada_minutos = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.origen.ciudad} -> {self.destino.ciudad}"


class Bus(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    marca_modelo = models.CharField(max_length=100)
    capacidad_asientos = models.PositiveIntegerField()

    def __str__(self):
        return f"Bus {self.patente} ({self.marca_modelo})"


class Servicio(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    fecha_hora_salida = models.DateTimeField()
    fecha_hora_llegada = models.DateTimeField()

    def __str__(self):
        return f"Servicio #{self.id} | {self.ruta} - {self.fecha_hora_salida.strftime('%Y-%m-%d %H:%M')}"


class AsientoServicio(models.Model):
    TIPO_CHOICES = (
        ('SEMICAMA', 'Semicama'),
        ('CAMA', 'Cama'),
    )
    ESTADO_CHOICES = (
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADO', 'Ocupado'),
    )

    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='asientos')
    numero_asiento = models.PositiveIntegerField()
    tipo_asiento = models.CharField(max_length=20, choices=TIPO_CHOICES, default='SEMICAMA')
    precio = models.DecimalField(max_length=10, max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')

    class Meta:
        unique_together = ('servicio', 'numero_asiento')

    def __str__(self):
        return f"Asiento {self.numero_asiento} ({self.tipo_asiento}) - Servicio #{self.servicio.id}"


# ---------------------------------------------------------------------
# 3. CARRO DE PASAJES PERSISTENTE (1:1 CON USUARIO)
# ---------------------------------------------------------------------
class CarroPasajes(models.Model):
    usuario = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='carro')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carro de {self.usuario.username}"


class ItemCarro(models.Model):
    carro = models.ForeignKey(CarroPasajes, on_delete=models.CASCADE, related_name='items')
    asiento_servicio = models.ForeignKey(AsientoServicio, on_delete=models.CASCADE)
    pasajero_nombre = models.CharField(max_length=150)
    pasajero_rut_pasaporte = models.CharField(max_length=20)

    class Meta:
        unique_together = ('carro', 'asiento_servicio')


# ---------------------------------------------------------------------
# 4. TRANSACCIÓN, BOLETOS Y ESTADOS
# ---------------------------------------------------------------------
class Venta(models.Model):
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
        ('COMPLETADO', 'Completado'),
    )

    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    codigo_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f"Venta {self.codigo_uuid} - Estado: {self.estado}"


class Boleto(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='boletos')
    asiento_servicio = models.ForeignKey(AsientoServicio, on_delete=models.CASCADE)
    pasajero_nombre = models.CharField(max_length=150)
    pasajero_rut_pasaporte = models.CharField(max_length=20)
    precio_historico = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_boleto = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Boleto {self.codigo_boleto} ({self.pasajero_nombre})"