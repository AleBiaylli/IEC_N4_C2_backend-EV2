from django.core.management.base import BaseCommand
from api.models import Teacher, Course, Student, StudentCourse

class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de prueba iniciales (Seed Data)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpiando base de datos...")
        StudentCourse.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()

        self.stdout.write("Insertando datos de prueba...")

        # 1. Crear Docentes
        t1 = Teacher.objects.create(first_name="Roberto", last_name="Gómez")
        t2 = Teacher.objects.create(first_name="Ana", last_name="Martínez")

        # 2. Crear Asignaturas
        c1 = Course.objects.create(name="Programación Web", teacher=t1)
        c2 = Course.objects.create(name="Bases de Datos", teacher=t1)
        c3 = Course.objects.create(name="Sistemas Operativos", teacher=t2)

        # 3. Crear Estudiantes
        s1 = Student.objects.create(first_name="Carlos", last_name="Pérez")
        s2 = Student.objects.create(first_name="María", last_name="López")

        # 4. Crear Inscripciones
        StudentCourse.objects.create(student=s1, course=c1)
        StudentCourse.objects.create(student=s1, course=c2)
        StudentCourse.objects.create(student=s2, course=c3)

        self.stdout.write(self.style.SUCCESS("¡Seed data cargado con éxito!"))