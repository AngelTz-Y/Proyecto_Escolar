from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now


HORAS_DISPONIBLES = [
    ('8:00-9:00', '8:00-9:00'),
    ('9:00-10:00', '9:00-10:00'),
    ('10:00-11:00', '10:00-11:00'),
    ('11:00-12:00', '11:00-12:00'),
    ('12:00-13:00', '12:00-13:00'),
    ('14:00-15:00', '14:00-15:00'),
    ('15:00-16:00', '15:00-16:00'),
]

DIAS_SEMANA = [
    ('Lunes', 'Lunes'),
    ('Martes', 'Martes'),
    ('Miércoles', 'Miércoles'),
    ('Jueves', 'Jueves'),
    ('Viernes', 'Viernes'),
    ('Sábado', 'Sábado'),
    ('Domingo', 'Domingo'),
]

class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Apoderado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='apoderado')
    rut = models.CharField(max_length=12, unique=True, blank=True, null=True)  # Campo opcional
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.correo}"


class Profesor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profesor')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    asignaturas = models.ManyToManyField(Asignatura, related_name='profesores')
    cursos = models.ManyToManyField('Curso', related_name='profesores_asignados', blank=True)  # Evitamos el conflicto con related_name

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

from django.core.exceptions import ValidationError

class ProfesorJefe(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True, default=1)
    grado_asignado = models.CharField(max_length=10, blank=True, null=True)  # Nuevo campo

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.correo})"
    
    
class Estudiante(models.Model):
    apoderado = models.ForeignKey(Apoderado, on_delete=models.CASCADE, related_name='estudiantes')
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='estudiante')
    rut = models.CharField(max_length=12, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    nivel_educativo = models.CharField(max_length=50)
    curso = models.ForeignKey('Curso', on_delete=models.SET_NULL, null=True, blank=True, related_name="estudiantes_asignados")  # Renombrado
    asignaturas = models.ManyToManyField(Asignatura, related_name='estudiantes', blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - Nivel: {self.nivel_educativo}"


class Curso(models.Model):
    GRADOS = [
        ('1-A', '1° Básico A'), ('2-A', '2° Básico A'), ('3-A', '3° Básico A'),
        ('4-A', '4° Básico A'), ('5-A', '5° Básico A'), ('6-A', '6° Básico A'),
        ('7-A', '7° Básico A'), ('8-A', '8° Básico A'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    asignaturas = models.ManyToManyField(Asignatura, related_name="cursos")
    grado = models.CharField(max_length=10, choices=GRADOS, unique=True)
    profesor_jefe = models.ForeignKey(ProfesorJefe, on_delete=models.CASCADE, related_name="cursos", null=True, blank=True)
    estudiantes = models.ManyToManyField(Estudiante, related_name="cursos", blank=True)
    limite_estudiantes = models.PositiveIntegerField(default=1)  # Límite por defecto de estudiantes

    def __str__(self):
        return f"{self.nombre} ({self.get_grado_display()})"

    @property
    def esta_lleno(self):
        """Comprueba si el curso alcanzó el límite de estudiantes."""
        return self.estudiantes.count() >= self.limite_estudiantes




class HorarioEscolar(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='horarios')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    dia = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora = models.CharField(max_length=20, choices=HORAS_DISPONIBLES)

    def __str__(self):
        return f"{self.dia} {self.hora} - {self.asignatura.nombre}"

class Nota(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='notas')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    nota1 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota2 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota3 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota4 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota5 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota6 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota7 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    nota8 = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Notas de {self.estudiante.nombre} en {self.asignatura.nombre}"

class Evaluacion(models.Model):
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha = models.DateField()
    descripcion = models.TextField()

    def __str__(self):
        return f"Evaluación en {self.asignatura.nombre} el {self.fecha}"

class Asistencia(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    presente = models.BooleanField()

    def __str__(self):
        return f"Asistencia de {self.estudiante.nombre} el {self.fecha}"

class Observacion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='observaciones')
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE, related_name='observaciones')
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Observación de {self.profesor.nombre} a {self.estudiante.nombre} el {self.fecha}"

class Administrador(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='administrador')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)

    def __str__(self):
        return f"Administrador: {self.nombre} {self.apellido}"

class RegistroCambios(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Supongamos que el usuario con ID 1 es el predeterminado
    fecha = models.DateTimeField(auto_now=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.usuario.username} - {self.descripcion} - {self.fecha}"

class Sesion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    inicio_sesion = models.DateTimeField(default=timezone.now)
    fin_sesion = models.DateTimeField(blank=True, null=True)

    def cerrar_sesion(self):
        self.fin_sesion = timezone.now()
        self.save()

    def __str__(self):
        return f"Sesión de {self.usuario.username} - {self.inicio_sesion} a {self.fin_sesion}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_seen_changes = models.DateTimeField(default=now)

    def __str__(self):
        return self.user.username