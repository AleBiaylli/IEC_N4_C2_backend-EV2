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
from django.urls import path, re_path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views import (
    login_view, 
    home_view, 
    teachers_view, 
    courses_view, 
    students_view,
    custom_page_not_found_view
)

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),

    # 1. RUTA DE LOGIN PERSONALIZADO
    path('login/', login_view, name='login'),

    # 2. RUTAS FRONTEND (Vistas HTML)
    path('', home_view, name='home'),
    path('teachers/', teachers_view, name='teachers_list'),
    path('teachers/html/', teachers_view, name='teachers-list-html'),
    path('courses/', courses_view, name='courses_list'),
    path('courses/html/', courses_view, name='courses-list-html'),
    path('students/', students_view, name='students_list'),
    path('students/html/', students_view, name='students-list-html'),

    # 3. ENDPOINTS API REST Y JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # 4. REGISTRO OBLIGATORIO DEL NAMESPACE DE DRF
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # 5. RUTAS DE TU API REST
    path('api/', include('api.urls')),

    # 6. RUTA COMODÍN (CATCH-ALL) PARA CUALQUIER PALABRA O RUTA NO REGISTRADA
    # Importante: Debe ir OBLIGATORIAMENTE al final de la lista
    re_path(r'^.*$', custom_page_not_found_view, name='catch_all_404'),
]

# Manejador global por defecto de Django
handler404 = 'api.views.custom_page_not_found_view'