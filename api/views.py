from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Teacher, Course, Student, StudentCourse
from .serializer import (
    TeacherSerializer, CourseSerializer,
    StudentSerializer, StudentCourseSerializer
)

# =====================================================================
# 1. ENDPOINTS DE LA API REST (VIEWSETS)
# =====================================================================

class TeacherViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Profesores.
    Permite lecturas (GET) públicas, pero exige JWT activo para 
    crear, editar o eliminar (POST, PUT, DELETE).
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Cursos.
    Exige autenticación mediante Token JWT para todas las operaciones.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar Estudiantes.
    Exige autenticación mediante Token JWT para todas las operaciones.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class StudentCourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar inscripciones de Estudiantes en Cursos.
    Exige autenticación mediante Token JWT.
    """
    queryset = StudentCourse.objects.all()
    serializer_class = StudentCourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


# =====================================================================
# 2. VISTAS HTML DEL FRONTEND (RENDERIZADO DE PLANTILLAS)
# =====================================================================

def home_view(request):
    """Renderiza el Panel Principal / Dashboard."""
    return render(request, 'index.html')


def login_view(request):
    """Renderiza el inicio de sesión personalizado con Bootstrap."""
    return render(request, 'login_custom.html')


def teachers_view(request):
    """Renderiza la vista pública del listado de Profesores."""
    return render(request, 'teachers_list.html')


def courses_view(request):
    """
    Renderiza la vista del listado de Cursos.
    La protección de acceso se valida en el cliente (JS) mediante el JWT.
    """
    return render(request, 'courses_list.html')


def students_view(request):
    """
    Renderiza la vista del listado de Estudiantes.
    La protección de acceso se valida en el cliente (JS) mediante el JWT.
    """
    return render(request, 'students_list.html')


def custom_page_not_found_view(request, exception=None):
    """
    Vista personalizada para capturar rutas inexistentes (Error 404).
    """
    return render(request, '404.html', status=404)