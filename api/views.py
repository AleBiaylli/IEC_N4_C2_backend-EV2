"""
1. Endpoints API RESTful (Servicios, Carro Persistente, Checkout, Historial y Admin).
2. Vistas HTML para el Portal Web de clientes con el Footer obligatorio del alumno.
"""

from decimal import Decimal
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import (
    CustomUser, Terminal, Ruta, Bus, Servicio, 
    AsientoServicio, CarroPasajes, ItemCarro, Venta, Boleto
)
from .serializers import (
    CustomTokenObtainPairSerializer, TerminalSerializer, RutaSerializer,
    BusSerializer, ServicioSerializer, AsientoServicioSerializer,
    CarroPasajesSerializer, ItemCarroSerializer, VentaSerializer, BoletoSerializer
)

# Obtener el modelo de usuario activo (CustomUser)
User = get_user_model()

# Constante global con la información institucional del alumno para el Footer
STUDENT_CONTEXT = {
    'student_name': 'Alexander Biaylli Lagos Allilef',
    'student_section': 'Sección IEC_N4_C2',
    'student_year': '2026'
}


# ===========================================================================
# SECCIÓN I: PERMISOS Y AUTENTICACIÓN JWT (API REST)
# ===========================================================================

class IsAdminFlota(permissions.BasePermission):
    """Permiso personalizado que restringe el acceso solo a Administradores de Flota."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', None) == 'ADMIN_FLOTA'
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Endpoint de Login JWT que expide tokens con los claims del rol."""
    serializer_class = CustomTokenObtainPairSerializer


# ===========================================================================
# SECCIÓN II: VISTAS DE AUTENTICACIÓN PARA LA INTERFAZ HTML
# ===========================================================================

def registro_web_view(request):
    """Permite registrar un nuevo cliente asignando por defecto el rol PASAJERO."""
    if request.user.is_authenticated:
        return redirect('buscar_pasajes')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html', STUDENT_CONTEXT)

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está registrado.')
            return render(request, 'registro.html', STUDENT_CONTEXT)

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'registro.html', STUDENT_CONTEXT)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        if hasattr(user, 'role'):
            user.role = 'PASAJERO'
            user.save()

        login(request, user)
        messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido, {user.first_name}.')
        return redirect('buscar_pasajes')

    return render(request, 'registro.html', STUDENT_CONTEXT)


def login_web_view(request):
    """Permite iniciar sesión aceptando tanto Nombre de Usuario como Correo Electrónico."""
    if request.user.is_authenticated:
        return redirect('buscar_pasajes')

    if request.method == 'POST':
        login_input = request.POST.get('login_input', '').strip()
        password = request.POST.get('password', '')

        user_obj = User.objects.filter(
            Q(username__iexact=login_input) | Q(email__iexact=login_input)
        ).first()

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                rol_actual = getattr(user, 'role', 'PASAJERO')
                
                # Saludo adaptado según el rol
                if rol_actual == 'ADMIN_FLOTA':
                    messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.username}! [ADMIN FLOTA]')
                else:
                    messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.username}!')
                    
                return redirect('buscar_pasajes')

        messages.error(request, 'Usuario/correo o contraseña incorrectos.')

    return render(request, 'login.html', STUDENT_CONTEXT)


def logout_web_view(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    return redirect('home')


# ===========================================================================
# SECCIÓN III: ENDPOINTS API RESTFUL
# ===========================================================================

class ServicioViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint público para buscar e inspeccionar itinerarios de viajes."""
    queryset = Servicio.objects.all().order_by('fecha_hora_salida')
    serializer_class = ServicioSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ruta__origen', 'ruta__destino', 'ruta']

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def asientos(self, request, pk=None):
        servicio = self.get_object()
        asientos = servicio.asientos.all().order_by('numero_asiento')
        serializer = AsientoServicioSerializer(asientos, many=True)
        return Response(serializer.data)


class CarroPasajesView(APIView):
    """Gestiona el carro activo vinculado 1:1 con la base de datos PostgreSQL."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        carro, _ = CarroPasajes.objects.get_or_create(usuario=request.user)
        serializer = CarroPasajesSerializer(carro)
        return Response(serializer.data)

    def post(self, request):
        carro, _ = CarroPasajes.objects.get_or_create(usuario=request.user)
        asiento_id = request.data.get('asiento_servicio')
        pasajero_nombre = request.data.get('pasajero_nombre')
        pasajero_rut = request.data.get('pasajero_rut_pasaporte')

        if not all([asiento_id, pasajero_nombre, pasajero_rut]):
            return Response({'error': 'Faltan datos obligatorios del pasaje.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            asiento = AsientoServicio.objects.get(id=asiento_id)
        except AsientoServicio.DoesNotExist:
            return Response({'error': 'El asiento solicitado no existe.'}, status=status.HTTP_404_NOT_FOUND)

        if asiento.estado == 'OCUPADO':
            return Response({'error': 'El asiento ya se encuentra ocupado.'}, status=status.HTTP_400_BAD_REQUEST)

        item, _ = ItemCarro.objects.update_or_create(
            carro=carro,
            asiento_servicio=asiento,
            defaults={
                'pasajero_nombre': pasajero_nombre,
                'pasajero_rut_pasaporte': pasajero_rut
            }
        )
        return Response(ItemCarroSerializer(item).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        item_id = request.data.get('item_id')
        try:
            item = ItemCarro.objects.get(id=item_id, carro__usuario=request.user)
            item.delete()
            return Response({'mensaje': 'Pasaje removido del carro correctamente.'}, status=status.HTTP_200_OK)
        except ItemCarro.DoesNotExist:
            return Response({'error': 'El ítem especificado no pertenece a su carro.'}, status=status.HTTP_404_NOT_FOUND)


class CheckoutVentaView(APIView):
    """Procesa el checkout y emisión de boletos para Pasajeros."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        carro, _ = CarroPasajes.objects.get_or_create(usuario=request.user)
        items = carro.items.all()

        if not items.exists():
            return Response({'error': 'No hay pasajes seleccionados en el carro.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            monto_total = Decimal('0.00')
            asientos_a_procesar = []

            for item in items:
                asiento = AsientoServicio.objects.select_for_update().get(id=item.asiento_servicio.id)
                
                if asiento.estado == 'OCUPADO':
                    transaction.set_rollback(True)
                    return Response({
                        'error': f'El asiento #{asiento.numero_asiento} fue tomado por otro usuario.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                monto_total += asiento.precio
                asientos_a_procesar.append((asiento, item))

            venta = Venta.objects.create(
                usuario=request.user,
                monto_total=monto_total,
                estado='PAGADO'
            )

            for asiento, item in asientos_a_procesar:
                Boleto.objects.create(
                    venta=venta,
                    asiento_servicio=asiento,
                    pasajero_nombre=item.pasajero_nombre,
                    pasajero_rut_pasaporte=item.pasajero_rut_pasaporte,
                    precio_historico=asiento.precio
                )
                asiento.estado = 'OCUPADO'
                asiento.save()

            items.delete()
            return Response(VentaSerializer(venta).data, status=status.HTTP_201_CREATED)


class MisBoletosView(APIView):
    """Permite al Pasajero revisar el historial de sus boletos emitidos."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ventas = Venta.objects.filter(usuario=request.user).order_by('-fecha_venta')
        serializer = VentaSerializer(ventas, many=True)
        return Response(serializer.data)


class CambiarEstadoVentaView(APIView):
    """Permite al Administrador de Flota (ADMIN_FLOTA) cambiar el estado de la Venta."""
    permission_classes = [IsAdminFlota]

    def patch(self, request, pk):
        try:
            venta = Venta.objects.get(pk=pk)
        except Venta.DoesNotExist:
            return Response({'error': 'Registro de venta no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        nuevo_estado = request.data.get('estado')
        if nuevo_estado not in dict(Venta.ESTADO_CHOICES):
            return Response({'error': 'Estado de venta no válido.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if nuevo_estado == 'CANCELADO' and venta.estado != 'CANCELADO':
                for boleto in venta.boletos.all():
                    asiento = boleto.asiento_servicio
                    asiento.estado = 'DISPONIBLE'
                    asiento.save()

            venta.estado = nuevo_estado
            venta.save()

        return Response(VentaSerializer(venta).data, status=status.HTTP_200_OK)


# ===========================================================================
# SECCIÓN IV: VISTAS HTML PARA EL PORTAL CLIENTE (GUI)
# ===========================================================================

def home_view(request):
    """Renderiza la portada principal tipo portal comercial."""
    terminales = Terminal.objects.values_list('ciudad', flat=True).distinct().order_by('ciudad')
    context = {
        'terminales': terminales,
        **STUDENT_CONTEXT
    }
    return render(request, 'base.html', context)


def buscar_pasajes_view(request):
    """Vista de búsqueda de pasajes con filtrado entre ciudades."""
    servicios = Servicio.objects.select_related('ruta__origen', 'ruta__destino', 'bus').all().order_by('fecha_hora_salida')
    terminales = Terminal.objects.values_list('ciudad', flat=True).distinct().order_by('ciudad')

    origen = request.GET.get('origen', '').strip()
    destino = request.GET.get('destino', '').strip()
    fecha_ida = request.GET.get('fecha_ida', '').strip()

    if origen:
        servicios = servicios.filter(ruta__origen__ciudad__icontains=origen)
    if destino:
        servicios = servicios.filter(ruta__destino__ciudad__icontains=destino)

    if fecha_ida:
        servicios_fecha = servicios.filter(fecha_hora_salida__date=fecha_ida)
        if servicios_fecha.exists():
            servicios = servicios_fecha

    context = {
        'servicios': servicios,
        'terminales': terminales,
        **STUDENT_CONTEXT
    }
    return render(request, 'buscar_pasajes.html', context)


def detalle_asientos_view(request, servicio_id):
    """Vista HTML para la selección gráfica de asientos de un servicio."""
    servicio = get_object_or_404(Servicio, id=servicio_id)
    asientos = AsientoServicio.objects.filter(servicio=servicio).order_by('numero_asiento')
    
    context = {
        'servicio': servicio,
        'asientos': asientos,
        **STUDENT_CONTEXT
    }
    return render(request, 'reserva_asientos.html', context)


@login_required
def mi_carro_view(request):
    """Muestra el carro de compras activo utilizando el modelo CarroPasajes."""
    carro, _ = CarroPasajes.objects.get_or_create(usuario=request.user)
    
    items = carro.items.select_related(
        'asiento_servicio__servicio__ruta__origen',
        'asiento_servicio__servicio__ruta__destino',
        'asiento_servicio__servicio__bus'
    ).all()

    total = Decimal('0.00')
    for item in items:
        asiento = item.asiento_servicio
        precio = getattr(asiento, 'precio', Decimal('12000.00'))
        item.precio_calculado = precio
        total += precio

    context = {
        'carro': carro,
        'items': items,
        'total': total,
        **STUDENT_CONTEXT
    }
    return render(request, 'mi_carro.html', context)


@login_required
def eliminar_item_carro_view(request, item_id):
    """Elimina un asiento/ítem del carro de compras del usuario."""
    item = get_object_or_404(ItemCarro, id=item_id, carro__usuario=request.user)
    item.delete()
    messages.success(request, 'Pasaje eliminado del carro de compras.')
    return redirect('mi_carro')


@login_required
def editar_item_carro_view(request, item_id):
    """
    Permite modificar la hora o el asiento seleccionado del pasaje.
    Liberamos el ítem actual y redirigimos al selector de asientos del servicio.
    """
    item = get_object_or_404(ItemCarro, id=item_id, carro__usuario=request.user)
    servicio_id = item.asiento_servicio.servicio.id
    item.delete()
    messages.info(request, 'Selecciona la nueva hora o número de asiento disponible.')
    return redirect('detalle_asientos', servicio_id=servicio_id)


@login_required
def pago_web_view(request):
    """Paso 2: Formulario de Pago que despliega el resumen de los asientos en el carro."""
    carro, _ = CarroPasajes.objects.get_or_create(usuario=request.user)
    items = carro.items.select_related(
        'asiento_servicio__servicio__ruta__origen',
        'asiento_servicio__servicio__ruta__destino'
    ).all()

    if not items.exists():
        messages.warning(request, 'Tu carro de compras está vacío.')
        return redirect('buscar_pasajes')

    total = Decimal('0.00')
    for item in items:
        total += getattr(item.asiento_servicio, 'precio', Decimal('12000.00'))

    context = {
        'carro': carro,
        'items': items,
        'total': total,
        **STUDENT_CONTEXT
    }
    return render(request, 'pago.html', context)


@login_required
def confirmacion_compra_view(request, venta_id):
    """Paso 3: Muestra el detalle del comprobante de venta y boletos generados."""
    venta = get_object_or_404(Venta, id=venta_id, usuario=request.user)
    boletos = venta.boletos.select_related(
        'asiento_servicio__servicio__ruta__origen',
        'asiento_servicio__servicio__ruta__destino',
        'asiento_servicio__servicio__bus'
    ).all()

    context = {
        'venta': venta,
        'boletos': boletos,
        **STUDENT_CONTEXT
    }
    return render(request, 'confirmacion.html', context)


def pagina_no_encontrada_view(request, exception=None, undefined_path=None):
    """
    Muestra la vista personalizada 404 con el contexto institucional del alumno
    ante cualquier ruta/dirección mal ingresada.
    """
    return render(request, '404.html', STUDENT_CONTEXT, status=404)


# ===========================================================================
# SECCIÓN V: ACCIONES DE FORMULARIO HTML (INTEGRACIÓN CON LA INTERFAZ)
# ===========================================================================

def agregar_al_carro_html(request, asiento_id):
    """Agrega un asiento al carro desde la plantilla HTML."""
    if request.method == 'POST':
        asiento = get_object_or_404(AsientoServicio, id=asiento_id)
        if asiento.estado == 'DISPONIBLE':
            carro, _ = CarroPasajes.objects.get_or_create(usuario=request.user if request.user.is_authenticated else None)
            if request.user.is_authenticated:
                ItemCarro.objects.update_or_create(
                    carro=carro,
                    asiento_servicio=asiento,
                    defaults={
                        'pasajero_nombre': request.POST.get('pasajero_nombre', request.user.username),
                        'pasajero_rut_pasaporte': request.POST.get('pasajero_rut', '11111111-1')
                    }
                )
            return redirect('mi_carro')
    return redirect('buscar_pasajes')


def procesar_checkout_html(request):
    """
    Ejecuta la compra atómica de los pasajes seleccionados en el carro
    y redirige al usuario a la vista de confirmación del boleto.
    """
    if request.method == 'POST' and request.user.is_authenticated:
        carro, _ = CarroPasajes.objects.get_or_create(usuario=request.user)
        items = carro.items.select_related('asiento_servicio').all()

        if items.exists():
            with transaction.atomic():
                monto_total = Decimal('0.00')
                asientos_a_procesar = []

                for item in items:
                    asiento = AsientoServicio.objects.select_for_update().get(id=item.asiento_servicio.id)
                    if asiento.estado == 'OCUPADO':
                        transaction.set_rollback(True)
                        messages.error(request, f'El asiento #{asiento.numero_asiento} ya fue reservado por otro usuario.')
                        return redirect('mi_carro')

                    monto_total += asiento.precio
                    asientos_a_procesar.append((asiento, item))

                venta = Venta.objects.create(
                    usuario=request.user,
                    monto_total=monto_total,
                    estado='PAGADO'
                )

                for asiento, item in asientos_a_procesar:
                    Boleto.objects.create(
                        venta=venta,
                        asiento_servicio=asiento,
                        pasajero_nombre=item.pasajero_nombre,
                        pasajero_rut_pasaporte=item.pasajero_rut_pasaporte,
                        precio_historico=asiento.precio
                    )
                    asiento.estado = 'OCUPADO'
                    asiento.save()

                items.delete()

                messages.success(request, '¡Pago procesado exitosamente!')
                return redirect('confirmacion_compra', venta_id=venta.id)

    return redirect('mi_carro')