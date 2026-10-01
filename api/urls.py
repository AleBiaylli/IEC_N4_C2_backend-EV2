"""
Define los endpoints requeridos para la API REST y las rutas Web para el Portal de Pasajeros.
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    CustomTokenObtainPairView,
    ServicioViewSet,
    CarroPasajesView,
    CheckoutVentaView,
    MisBoletosView,
    CambiarEstadoVentaView,
)

# Router para vistas API de servicios/itinerarios
router = DefaultRouter()
router.register(r'servicios', ServicioViewSet, basename='servicios')

urlpatterns = [
    # -----------------------------------------------------------------------
    # 1. VISTAS HTML DEL PORTAL WEB (GUI)
    # -----------------------------------------------------------------------
    path('', views.home_view, name='home'),
    path('buscar-pasajes/', views.buscar_pasajes_view, name='buscar_pasajes'),
    path('asientos/<int:servicio_id>/', views.detalle_asientos_view, name='detalle_asientos'),
    
    # Flujo de Carro, Edición y Pago (Pasos 1, 2 y 3)
    path('mi-carro/', views.mi_carro_view, name='mi_carro'),
    path('carro/agregar/<int:asiento_id>/', views.agregar_al_carro_html, name='agregar_al_carro_html'),
    path('carro/eliminar/<int:item_id>/', views.eliminar_item_carro_view, name='eliminar_item_carro'),
    path('carro/editar/<int:item_id>/', views.editar_item_carro_view, name='editar_item_carro'),
    path('pago/', views.pago_web_view, name='pago_web'),
    path('checkout/procesar/', views.procesar_checkout_html, name='procesar_checkout'),
    path('confirmacion/<int:venta_id>/', views.confirmacion_compra_view, name='confirmacion_compra'),
    
    # Autenticación Web
    path('login/', views.login_web_view, name='login_web'),
    path('logout/', views.logout_web_view, name='logout_web'),
    path('registro/', views.registro_web_view, name='registro_web'),

    # -----------------------------------------------------------------------
    # 2. AUTENTICACIÓN Y JWT CON ROLES (API REST)
    # -----------------------------------------------------------------------
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # -----------------------------------------------------------------------
    # 3. ENDPOINTS API REST PASAJERO
    # -----------------------------------------------------------------------
    path('carro-pasajes/', CarroPasajesView.as_view(), name='carro-pasajes'),
    path('ventas/checkout/', CheckoutVentaView.as_view(), name='ventas-checkout'),
    path('mis-boletos/', MisBoletosView.as_view(), name='mis-boletos'),

    # -----------------------------------------------------------------------
    # 4. ENDPOINTS API REST ADMINISTRADOR DE FLOTA
    # -----------------------------------------------------------------------
    path('ventas/<int:pk>/estado/', CambiarEstadoVentaView.as_view(), name='cambiar-estado-venta'),

    # -----------------------------------------------------------------------
    # 5. RUTAS DEL ROUTER API (/servicios/)
    # -----------------------------------------------------------------------
    path('', include(router.urls)),

    # -----------------------------------------------------------------------
    # 6. RE_PATH COMODÍN PARA DIRECCIONES MAL ESCRITAS / ERROR 404
    # -----------------------------------------------------------------------
    re_path(r'^.*$', views.pagina_no_encontrada_view, name='404_catched'),
]