from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeacherViewSet, 
    CourseViewSet, 
    StudentViewSet, 
    StudentCourseViewSet
)

# Router para los endpoints REST de Django REST Framework
router = DefaultRouter()
router.register('teachers', TeacherViewSet, basename='teacher')
router.register('courses', CourseViewSet, basename='course')
router.register('students', StudentViewSet, basename='student')
router.register('student-courses', StudentCourseViewSet, basename='studentcourse')

urlpatterns = [
    # Mapea automáticamente las rutas /api/teachers/, /api/courses/, etc.
    path('', include(router.urls)),
]