from django.db.models.signals import post_migrate, post_delete, post_save
from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from .models import *


@receiver(post_delete, sender=Estudiante)
def eliminar_apoderado_si_no_hijos(sender, instance, **kwargs):
    """Elimina al apoderado si ya no tiene hijos registrados."""
    apoderado = instance.apoderado
    if not Estudiante.objects.filter(apoderado=apoderado).exists():
        user = apoderado.usuario
        apoderado.delete()  # Eliminar el modelo Apoderado
        user.delete()       # Eliminar el usuario asociado

@receiver(post_migrate)
def create_user_groups_and_superadmin(sender, **kwargs):
    """Crea los grupos de usuario (Estudiante, Apoderado, Profesor, Administrador) 
       y asocia el superusuario al grupo Administrador por defecto."""

    # Crear los grupos si no existen
    grupos = ['Estudiante', 'Apoderado', 'Profesor', 'Administrador']
    for grupo in grupos:
        Group.objects.get_or_create(name=grupo)

    # Crear el superusuario por defecto
    superuser_username = 'admin'
    superuser_password = 'admin'
    superuser_email = 'admin@example.com'

    superuser, created = User.objects.get_or_create(
        username=superuser_username,
        defaults={
            'password': superuser_password,
            'email': superuser_email,
            'is_superuser': True,
            'is_staff': True
        }
    )

    if created:
        superuser.set_password(superuser_password)  # Asegurar el hash de la contraseña
        superuser.save()
        print(f"Superusuario '{superuser_username}' creado con contraseña predeterminada.")
    else:
        print(f"Superusuario '{superuser_username}' ya existe.")

    # Asociar el superusuario al grupo "Administrador"
    administrador_group = Group.objects.get(name='Administrador')
    if administrador_group not in superuser.groups.all():
        superuser.groups.add(administrador_group)
        print(f"Superusuario '{superuser_username}' añadido al grupo 'Administrador'.")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
        
        
@receiver(post_migrate)
def crear_asignaturas_predeterminadas(sender, **kwargs):
    asignaturas_predeterminadas = [
        'Lenguaje', 'Matemática', 'Ciencias Naturales',
        'Inglés', 'Historia', 'Música'
    ]
    for asignatura in asignaturas_predeterminadas:
        Asignatura.objects.get_or_create(nombre=asignatura)