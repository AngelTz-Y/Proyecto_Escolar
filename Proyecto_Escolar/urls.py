"""
URL configuration for Proyecto_Escolar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from App_Escolar.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name="inicio"),
    path('login/', login, name="login"),
    path("registrarse/", registro, name="registro"),
    path('logout/', cerrar_sesion, name='logout'),
    path('estudiante/<int:estudiante_id>/dashboard/', estudiante_dashboard, name='estudiante_dashboard'),
    path('perfil_estudiantil/<int:estudiante_id>/', perfil_estudiantil, name="perfil_estudiantil"),
    path('estudiante/<int:estudiante_id>/asignaturas/', asignaturas, name='asignaturas'),
    path('estudiante/<int:estudiante_id>/horario/', horario_escolar, name='horario_escolar'),
    path('login_estudiante/', login_estudiante, name="login_estudiante"),
    path('administrador_dashboard/', administrador_dashboard, name='administrador_dashboard'),
    path('gestionar_usuarios/', gestionar_usuarios, name='gestionar_usuarios'),
    path('gestion_usuarios/', listar_usuarios, name='listar_usuarios'),
    path('listar_estudiantes/', listar_estudiantes, name='listar_estudiantes'),
    path('listar_profesores/', listar_profesores, name='listar_profesores'),
    path('listar_administradores/', listar_administradores, name='listar_administradores'),
    path('administrador_dashboard/crear_cuenta_profe/', crear_cuenta_profesor, name='crear_cuenta_profesor'),
    path('panel_profesor/', panel_profesor, name='profesor_dashboard'),
    path('modificar/estudiante/<int:estudiante_id>/', modificar_estudiante, name='modificar_estudiante'),
    path('eliminar/estudiante/<int:estudiante_id>/', eliminar_estudiante, name='eliminar_estudiante'),
    path('registro_cambios/', historial_cambios, name='registro_cambios'),
    path('resetear-contrasena/<int:estudiante_id>/', resetear_contrasena_estudiante, name='resetear_contrasena'),
    path('crear-curso/', crear_curso, name='crear_curso'),
    path('listar-cursos/', listar_cursos, name='listar_cursos'),
    path('gestionar-cursos/', gestionar_cursos, name='gestionar_cursos'),
    path('crear-profesor-jefe/', crear_profesor_jefe, name='crear_profesor_jefe'),
    path('asignar-profesor/', asignar_profesor, name='asignar_profesor'),
    path('asignar-estudiante/', asignar_estudiante, name='asignar_estudiante'),
    path('gestionar-asignaciones/', gestionar_asignaciones, name='gestionar_asignaciones'),
    path('listar-cursos/', listar_cursos, name='listar_cursos'),

    
]
