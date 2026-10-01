"""
URL configuration for IEC_N4_C2_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for IEC_N4_C2_backend project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.views import (
    home_view, 
    buscar_pasajes_view, 
    detalle_asientos_view, 
    mi_carro_view,
    agregar_al_carro_html,
    eliminar_item_carro_view,
    editar_item_carro_view,
    pago_web_view,
    procesar_checkout_html,
    confirmacion_compra_view,
    login_web_view,
    logout_web_view,
    registro_web_view,
    pagina_no_encontrada_view
)

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Rutas del Portal Web HTML
    path('', home_view, name='home'),
    path('login/', login_web_view, name='login_web'),
    path('logout/', logout_web_view, name='logout_web'),
    path('registro/', registro_web_view, name='registro_web'),
    
    path('buscar-pasajes/', buscar_pasajes_view, name='buscar_pasajes'),
    path('reserva-asientos/<int:servicio_id>/', detalle_asientos_view, name='detalle_asientos'),
    
    # Flujo de Carro y Checkout
    path('mi-carro/', mi_carro_view, name='mi_carro'),
    path('carro/agregar/<int:asiento_id>/', agregar_al_carro_html, name='agregar_al_carro'),
    path('carro/eliminar/<int:item_id>/', eliminar_item_carro_view, name='eliminar_item_carro'),
    path('carro/editar/<int:item_id>/', editar_item_carro_view, name='editar_item_carro'),
    path('pago/', pago_web_view, name='pago_web'),
    path('carro/checkout/', procesar_checkout_html, name='procesar_checkout'),
    path('confirmacion/<int:venta_id>/', confirmacion_compra_view, name='confirmacion_compra'),

    # Endpoints API REST Backend y Swagger
    path('api/', include('api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Captura de rutas no coincidentes mediante re_path comodín
    re_path(r'^.*$', pagina_no_encontrada_view, name='404_catchall'),
]

# Manejador global de producción para respuestas HTTP 404
handler404 = 'api.views.pagina_no_encontrada_view'