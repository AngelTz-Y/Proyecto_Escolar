from django.contrib.auth import authenticate, login as auth_login, logout 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *# Importamos los modelos necesarios
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import datetime, timedelta

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')


# View de Registro
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from .models import Apoderado, Estudiante
from django.utils.timezone import now

from django.db import IntegrityError  # Importamos IntegrityError para manejar problemas de base de datos

def registro(request):
    if request.method == 'POST':
        # Datos del Apoderado
        rut_apoderado = request.POST.get('rut_apoderado', '').strip()
        nombre_apoderado = request.POST.get('nombre_apoderado', '').strip()
        apellido_apoderado = request.POST.get('apellido_apoderado', '').strip()
        correo_apoderado = request.POST.get('correo_apoderado', '').strip()
        telefono_apoderado = request.POST.get('telefono_apoderado', '').strip()

        # Datos del Estudiante
        estudiante_rut = request.POST.get('rut_estudiante', '').strip()
        estudiante_username = request.POST.get('estudiante_username', '').strip()
        password_estudiante = request.POST.get('password', '').strip()
        nombre_estudiante = request.POST.get('nombre_estudiante', '').strip()
        apellido_estudiante = request.POST.get('apellido_estudiante', '').strip()
        fecha_nacimiento_str = request.POST.get('fecha_nacimiento', '').strip()

        # Validar campos obligatorios
        if not all([rut_apoderado, estudiante_rut, estudiante_username, password_estudiante, nombre_estudiante, apellido_estudiante, fecha_nacimiento_str]):
            messages.error(request, 'Debe completar todos los campos obligatorios.')
            return render(request, 'registrarse.html')

        # Validar fecha de nacimiento
        fecha_nacimiento = parse_date(fecha_nacimiento_str)
        if not fecha_nacimiento:
            messages.error(request, 'La fecha de nacimiento tiene un formato incorrecto. Use el formato AAAA-MM-DD.')
            return render(request, 'registrarse.html')

        try:
            # Verificar si el RUT del estudiante ya existe
            if Estudiante.objects.filter(rut=estudiante_rut).exists():
                messages.error(request, 'El RUT del estudiante ya está registrado. Verifique los datos ingresados.')
                return render(request, 'registrarse.html')

            # Verificar si el apoderado ya existe
            apoderado = Apoderado.objects.filter(rut=rut_apoderado).first()

            if not apoderado:
                # Crear usuario y apoderado
                apoderado_usuario = User.objects.create_user(
                    username=f"apoderado_{rut_apoderado}",
                    password="apoderado123",
                    email=correo_apoderado
                )
                apoderado_usuario.first_name = nombre_apoderado
                apoderado_usuario.last_name = apellido_apoderado
                apoderado_usuario.save()

                grupo_apoderado = Group.objects.get(name='Apoderado')
                apoderado_usuario.groups.add(grupo_apoderado)

                apoderado = Apoderado.objects.create(
                    usuario=apoderado_usuario,
                    rut=rut_apoderado,
                    nombre=nombre_apoderado,
                    apellido=apellido_apoderado,
                    correo=correo_apoderado,
                    telefono=telefono_apoderado
                )

            # Crear usuario y estudiante
            estudiante_usuario = User.objects.create_user(
                username=estudiante_username,
                password=password_estudiante
            )
            estudiante_usuario.first_name = nombre_estudiante
            estudiante_usuario.last_name = apellido_estudiante
            estudiante_usuario.save()

            grupo_estudiante = Group.objects.get(name='Estudiante')
            estudiante_usuario.groups.add(grupo_estudiante)

            Estudiante.objects.create(
                apoderado=apoderado,
                usuario=estudiante_usuario,
                rut=estudiante_rut,
                nombre=nombre_estudiante,
                apellido=apellido_estudiante,
                fecha_nacimiento=fecha_nacimiento
            )

            # Registrar el cambio en el historial
            RegistroCambios.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                fecha=now(),
                descripcion=f"El apoderado {apoderado.nombre} {apoderado.apellido} registró al estudiante {nombre_estudiante} {apellido_estudiante}."
            )

            messages.success(request, 'Usuario registrado correctamente.')
            return redirect('login')

        except IntegrityError:
            messages.error(request, 'Usuario registrado correctamente.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado: {str(e)}')
            return render(request, 'registrarse.html')

    return render(request, 'registrarse.html')


# View de Login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Estudiante

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from App_Escolar.models import Apoderado, Estudiante

from django.contrib.auth.models import Group

from django.utils.timezone import now

def login(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Validar campos vacíos
        if not username or not password:
            messages.error(request, 'Por favor, ingrese su nombre de usuario y contraseña.')
            return render(request, 'login.html')

        # Cerrar cualquier sesión activa antes de autenticar
        if request.user.is_authenticated:
            logout(request)

        # Intentar autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Asegurarse de que el perfil existe
            profile, created = UserProfile.objects.get_or_create(user=user)

            # Iniciar sesión
            auth_login(request, user)

            # Verificar grupo del usuario y redirigir según el rol
            if user.groups.filter(name='Estudiante').exists():
                try:
                    estudiante = Estudiante.objects.get(usuario=user)
                    messages.success(request, 'Inicio de sesión exitoso. Bienvenido Estudiante.')
                    return redirect('estudiante_dashboard', estudiante_id=estudiante.id)
                except Estudiante.DoesNotExist:
                    messages.error(request, 'No se encontró información de estudiante asociada.')
                    return redirect('login')

            elif user.groups.filter(name='Apoderado').exists():
                try:
                    apoderado = Apoderado.objects.get(usuario=user)
                    messages.success(request, 'Inicio de sesión exitoso. Bienvenido Apoderado.')
                    return redirect('apoderado_dashboard')
                except Apoderado.DoesNotExist:
                    messages.error(request, 'No se encontró información de apoderado asociada.')
                    return redirect('login')

            elif user.groups.filter(name='Profesor').exists():
                messages.success(request, 'Inicio de sesión exitoso. Bienvenido Profesor.')
                return redirect('profesor_dashboard')

            elif user.groups.filter(name='Administrador').exists():
                messages.success(request, 'Inicio de sesión exitoso. Bienvenido Administrador.')
                return redirect('administrador_dashboard')

            else:
                messages.error(request, 'No tiene permisos para acceder al sistema.')
                return redirect('login')
        else:
            # Error de autenticación
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            return render(request, 'login.html')

    return render(request, 'login.html')

def historial_cambios(request):
    """Muestra el historial de cambios y actualiza el estado de vistos."""
    # Asegurarse de que el perfil de usuario existe
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Obtener los cambios
    cambios = RegistroCambios.objects.all().order_by('-fecha')

    # Marcar como nuevos solo los cambios posteriores a la última vez que el usuario los vio
    for cambio in cambios:
        cambio.es_nuevo = cambio.fecha > profile.last_seen_changes

    # Actualizar el timestamp para indicar que el usuario ya vio los cambios
    profile.last_seen_changes = now()
    profile.save()

    return render(request, 'historial_cambios.html', {'cambios': cambios})


def administrador_dashboard(request):
    return render(request, 'InterfazAdministrador/panel_admin.html')

def login_estudiante(request):
    return render(request, 'login_estudiante.html')


@login_required
def cerrar_sesion(request):
    # Buscar la sesión activa del usuario
    sesion = Sesion.objects.filter(usuario=request.user, fin_sesion__isnull=True).last()
    if sesion:
        sesion.cerrar_sesion()  # Registrar la hora de cierre de sesión

    # Crear un registro en el historial de cambios
    descripcion = f"El usuario {request.user.username} cerró sesión el {now().strftime('%d/%m/%Y %H:%M')}."
    RegistroCambios.objects.create(
        usuario=request.user,
        descripcion=descripcion,
        fecha=now()
    )
    
    # Cerrar sesión del usuario
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("inicio")

@login_required
def estudiante_dashboard(request, estudiante_id):
    # Obtener el estudiante
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    
    # Renderizar el template con solo la información del estudiante
    return render(request, 'InterfazEstudiante/estudiante.html', {
        'estudiante': estudiante
    })

@login_required
def horario_escolar(request, estudiante_id):
    # Obtener el estudiante por su ID
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    # Datos para el horario vacío
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    horas = [
        '8:00 - 9:00', '9:00 - 10:00', '10:00 - 11:00', '11:00 - 12:00',
        '12:00 - 13:00', '14:00 - 15:00', '15:00 - 16:00'
    ]

    # Renderizar el template con los datos
    return render(request, 'InterfazEstudiante/horario_escolar.html', {
        'estudiante': estudiante,
        'dias': dias,
        'horas': horas
    })
    
def perfil_estudiantil(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    # Verificar si el usuario tiene permiso para ver el perfil
    if (
        hasattr(request.user, 'apoderado') and request.user.apoderado == estudiante.apoderado
    ) or (
        hasattr(request.user, 'estudiante') and request.user.estudiante == estudiante
    ):
        apoderado = estudiante.apoderado
        return render(request, 'perfil_estudiantil.html', {
            'estudiante': estudiante,
            'apoderado': apoderado
        })
    
    # Redirigir si no tiene permisos
    messages.error(request, 'No tienes permiso para acceder a este perfil.')
    return redirect('inicio')
    
    
@login_required
def asignaturas(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    asignaturas = estudiante.asignaturas.all()
    return render(request, 'asignaturas_estudiante.html', {'asignaturas': asignaturas, 'estudiante': estudiante})

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def horario_escolar(request, estudiante_id, semana_offset=0):
    # Obtener el estudiante
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    
    # Calcular la semana actual basada en el offset
    fecha_actual = datetime.now()
    fecha_inicio_semana = fecha_actual + timedelta(weeks=semana_offset) - timedelta(days=fecha_actual.weekday())
    
    # Generar los días de la semana
    dias = [(fecha_inicio_semana + timedelta(days=i)).strftime('%A %d') for i in range(7)]
    
    # Horas del día
    horas = [
        '8:00-9:00', '9:00-10:00', '10:00-11:00', '11:00-12:00', 
        '12:00-13:00', '14:00-15:00', '15:00-16:00'
    ]
    
    return render(request, 'InterfazEstudiante/horario_escolar.html', {
        'estudiante': estudiante,
        'dias': dias,
        'horas': horas,
        'semana_offset': semana_offset,
    })
    
    

def gestionar_usuarios(request):
    """Vista principal para gestionar usuarios"""
    return render(request, 'InterfazAdministrador/gestionar_usuarios.html')

def listar_usuarios(request):
    """Vista para mostrar la gestión de lista de usuarios."""
    return render(request, 'InterfazAdministrador/listar_usuarios.html')

def listar_estudiantes(request):
    """Vista para listar estudiantes con su apoderado."""
    estudiantes = Estudiante.objects.select_related('apoderado')
    return render(request, 'InterfazAdministrador/Listado/listar_estudiante.html', {'estudiantes': estudiantes})

def listar_profesores(request):
    """Vista para listar profesores."""
    profesores = Profesor.objects.select_related('usuario')
    return render(request, 'InterfazAdministrador/Listado/listar_profesor.html', {'profesores': profesores})

def listar_administradores(request):
    """Vista para listar administradores."""
    administradores = User.objects.filter(groups__name='Administrador')
    return render(request, 'InterfazAdministrador/Listado/listar_administrador.html', {'administradores': administradores})

def crear_cuenta_profesor(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        # Validar que el nombre de usuario sea único
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso. Intente con otro.')
            return redirect('crear_cuenta_profesor')

        # Crear el usuario
        user = User.objects.create_user(username=username, password=password)

        # Asignar al grupo "Profesor"
        grupo_profesor, created = Group.objects.get_or_create(name='Profesor')
        user.groups.add(grupo_profesor)

        # Registrar el cambio en el historial
        descripcion = f'El administrador {request.user.username} creó una cuenta para el profesor "{username}" el {now().strftime("%d/%m/%Y %H:%M")}.'
        RegistroCambios.objects.create(
            usuario=request.user,
            descripcion=descripcion,
            fecha=now()
        )

        # Notificar éxito
        messages.success(request, f'La cuenta del profesor "{username}" se ha creado exitosamente.')
        return redirect('crear_cuenta_profesor')

    return render(request, 'InterfazAdministrador/registrar_profesor.html')
    
from django.db import IntegrityError

def panel_profesor(request):
    """
    Muestra el panel del profesor y permite completar los datos si no están completos.
    """
    if request.user.is_authenticated:
        # Verificar si ya existe un perfil de profesor asociado
        profesor, created = Profesor.objects.get_or_create(usuario=request.user)

        if request.method == 'POST':
            # Guardar los datos enviados por el formulario
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono', '')

            try:
                # Validar y guardar los datos
                if nombre and apellido and correo:
                    # Registrar cambios solo si hay modificaciones
                    cambios = []
                    if profesor.nombre != nombre:
                        cambios.append(f"Nombre cambiado de '{profesor.nombre}' a '{nombre}'")
                        profesor.nombre = nombre
                    if profesor.apellido != apellido:
                        cambios.append(f"Apellido cambiado de '{profesor.apellido}' a '{apellido}'")
                        profesor.apellido = apellido
                    if profesor.correo != correo:
                        cambios.append(f"Correo cambiado de '{profesor.correo}' a '{correo}'")
                        profesor.correo = correo
                    if profesor.telefono != telefono:
                        cambios.append(f"Teléfono cambiado de '{profesor.telefono}' a '{telefono}'")
                        profesor.telefono = telefono

                    profesor.save()

                    # Registrar en el historial de cambios
                    if cambios:
                        descripcion = f"El profesor {profesor.usuario.username} actualizó sus datos: " + "; ".join(cambios)
                        RegistroCambios.objects.create(
                            usuario=request.user,
                            descripcion=descripcion,
                            fecha=now()
                        )

                    messages.success(request, "Tus datos han sido actualizados correctamente.")
                else:
                    messages.error(request, "Por favor, completa todos los campos requeridos.")
            except IntegrityError:
                messages.error(request, "El correo ingresado ya está en uso. Por favor, utiliza otro correo.")
            return redirect('profesor_dashboard')

        # Comprobar si los datos están incompletos
        datos_incompletos = not (profesor.nombre and profesor.apellido and profesor.correo)

        return render(request, 'InterfazProfesor/panel_profesor.html', {
            'profesor': profesor,
            'datos_incompletos': datos_incompletos,
        })
    else:
        messages.error(request, "Debes iniciar sesión para acceder al panel.")
        return redirect('login')
    
    
def modificar_estudiante(request, estudiante_id):
    """
    Modifica los datos de un estudiante y registra los cambios realizados.
    """
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)

    if request.method == 'POST':
        cambios = []  # Lista para almacenar los cambios realizados
        nuevo_nombre = request.POST.get('nombre', estudiante.nombre)
        nuevo_apellido = request.POST.get('apellido', estudiante.apellido)
        nuevo_rut = request.POST.get('rut', estudiante.rut)
        nuevo_nivel = request.POST.get('nivel_educativo', estudiante.nivel_educativo)

        # Registrar los cambios realizados
        if estudiante.nombre != nuevo_nombre:
            cambios.append(f"Nombre cambiado de '{estudiante.nombre}' a '{nuevo_nombre}'")
            estudiante.nombre = nuevo_nombre
        if estudiante.apellido != nuevo_apellido:
            cambios.append(f"Apellido cambiado de '{estudiante.apellido}' a '{nuevo_apellido}'")
            estudiante.apellido = nuevo_apellido
        if estudiante.rut != nuevo_rut:
            cambios.append(f"RUT cambiado de '{estudiante.rut}' a '{nuevo_rut}'")
            estudiante.rut = nuevo_rut
        if estudiante.nivel_educativo != nuevo_nivel:
            cambios.append(f"Nivel Educativo cambiado de '{estudiante.nivel_educativo}' a '{nuevo_nivel}'")
            estudiante.nivel_educativo = nuevo_nivel

        estudiante.save()

        # Registrar los cambios en el historial
        if cambios:
            descripcion = f"El usuario {request.user.username} modificó el estudiante {estudiante.nombre} {estudiante.apellido}: " + "; ".join(cambios)
            RegistroCambios.objects.create(
                usuario=request.user,
                descripcion=descripcion,
                fecha=now()
            )

        messages.success(request, "El estudiante ha sido modificado correctamente.")
        return redirect('listar_estudiantes')

    return render(request, 'InterfazAdministrador/modificar/editar_estudiante.html', {'estudiante': estudiante})


def eliminar_estudiante(request, estudiante_id):
    """
    Elimina un estudiante y verifica si debe eliminar también al apoderado y su registro en User.
    Además, registra la eliminación en el historial de cambios.
    """
    try:
        estudiante = get_object_or_404(Estudiante, id=estudiante_id)
        apoderado = estudiante.apoderado  # Guarda el apoderado para verificar luego
        usuario_estudiante = estudiante.usuario  # Guarda el usuario relacionado con el estudiante
        
        # Registrar en el historial antes de eliminar
        descripcion = f"El usuario {request.user.username} eliminó al estudiante {estudiante.nombre} {estudiante.apellido}."
        RegistroCambios.objects.create(
            usuario=request.user,
            descripcion=descripcion,
            fecha=now()
        )
        
        # Elimina el estudiante
        estudiante.delete()
        usuario_estudiante.delete()
        messages.success(request, f"El estudiante {usuario_estudiante.username} ha sido eliminado.")
        
        # Verifica si el apoderado no tiene más estudiantes
        if not Estudiante.objects.filter(apoderado=apoderado).exists():
            usuario_apoderado = apoderado.usuario  # Guarda el usuario relacionado con el apoderado
            
            # Registrar en el historial la eliminación del apoderado
            descripcion = f"El usuario {request.user.username} eliminó al apoderado {apoderado.nombre} {apoderado.apellido}."
            RegistroCambios.objects.create(
                usuario=request.user,
                descripcion=descripcion,
                fecha=now()
            )
            
            apoderado.delete()  # Elimina el apoderado
            usuario_apoderado.delete()  # Elimina el usuario del apoderado
            messages.success(request, f"El apoderado {usuario_apoderado.username} ha sido eliminado, ya que no tiene estudiantes asociados.")
        
    except Exception as e:
        messages.error(request, f"Error al eliminar estudiante: {str(e)}")
    
    return redirect('listar_estudiantes')


def resetear_contrasena_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    usuario = estudiante.usuario

    if request.method == 'POST':
        nueva_contrasena = request.POST.get('nueva_contrasena', '').strip()

        if nueva_contrasena:
            # Cambiar la contraseña
            usuario.set_password(nueva_contrasena)
            usuario.save()

            # Registrar el cambio
            descripcion = (
                f"El administrador {request.user.username} reseteó la contraseña del estudiante "
                f"{estudiante.nombre} {estudiante.apellido} el {datetime.now().strftime('%d/%m/%Y %H:%M')}."
            )
            RegistroCambios.objects.create(
                usuario=request.user,
                descripcion=descripcion
            )

            messages.success(request, f"La contraseña del estudiante {estudiante.nombre} ha sido reseteada.")
            return redirect('listar_estudiantes')
        else:
            messages.error(request, "Debe ingresar una nueva contraseña.")

    return render(request, 'resetear_contrasena_estudiante.html', {'estudiante': estudiante})


def crear_curso(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        grado = request.POST.get('grado', '').strip()
        profesor_jefe_id = request.POST.get('profesor_jefe', '').strip()
        asignaturas_ids = request.POST.getlist('asignaturas')

        if nombre and grado and profesor_jefe_id:
            try:
                # Validar si el profesor jefe ya está asignado a otro curso
                profesor_jefe = ProfesorJefe.objects.get(id=profesor_jefe_id)
                if Curso.objects.filter(profesor_jefe=profesor_jefe).exists():
                    messages.error(request, f"El profesor jefe '{profesor_jefe.nombre} {profesor_jefe.apellido}' ya está asignado a otro curso. Por favor, seleccione otro.")
                    raise Exception("Profesor Jefe Asignado")

                # Validar si el grado ya está siendo usado por otro curso
                if Curso.objects.filter(grado=grado).exists():
                    messages.error(request, f"El grado '{grado}' ya está siendo utilizado por otro curso. Por favor, seleccione otro grado.")
                    raise Exception("Grado en Uso")

                # Validar si el curso ya tiene el límite de estudiantes
                curso_existente = Curso.objects.filter(grado=grado).first()
                if curso_existente and curso_existente.estudiantes.count() >= curso_existente.limite_estudiantes:
                    messages.error(request, f"El grado '{grado}' ya tiene el límite de estudiantes.")
                    raise Exception("Curso Lleno")

                # Asignar el grado al profesor jefe y crear el curso
                profesor_jefe.grado_asignado = grado  # Suponiendo que existe un campo en el modelo para almacenar el grado
                profesor_jefe.save()

                curso = Curso.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    grado=grado,
                    profesor_jefe=profesor_jefe
                )
                asignaturas = Asignatura.objects.filter(id__in=asignaturas_ids)
                curso.asignaturas.set(asignaturas)
                messages.success(request, f"El curso '{curso.nombre}' se ha creado exitosamente, y el profesor jefe ha sido asignado al grado '{curso.get_grado_display()}'.")
                return redirect('gestionar_cursos')

            except ProfesorJefe.DoesNotExist:
                messages.error(request, "El profesor jefe seleccionado no existe.")
            except Exception as e:
                print(e)

        else:
            messages.error(request, "Todos los campos son obligatorios.")

    # Enviar datos necesarios al formulario
    profesores_jefes = ProfesorJefe.objects.all()
    asignaturas = Asignatura.objects.all()
    grados = []
    for value, display in Curso.GRADOS:
        curso_existente = Curso.objects.filter(grado=value).first()
        grados.append({
            'grado': value,
            'display': display,
            'disabled': bool(curso_existente and curso_existente.estudiantes.count() >= curso_existente.limite_estudiantes)
        })

    return render(request, 'crear_curso.html', {
        'profesores_jefes': profesores_jefes,
        'asignaturas': asignaturas,
        'grados': grados,
    })

def listar_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'listar_cursos.html', {'cursos': cursos})


def gestionar_cursos(request):
    cursos = Curso.objects.all()
    profesores_jefes = ProfesorJefe.objects.all()
    return render(request, 'gestionar_cursos.html', {
        'cursos': cursos,
        'profesores_jefes': profesores_jefes
    })
    
def crear_profesor_jefe(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        apellido = request.POST.get('apellido').strip()
        correo = request.POST.get('correo').strip()
        telefono = request.POST.get('telefono', '').strip()

        if nombre and apellido and correo:
            if ProfesorJefe.objects.filter(correo=correo).exists():
                messages.error(request, 'Ya existe un profesor jefe con este correo.')
            else:
                # Validación: verificar si el curso seleccionado tiene menos de 4 estudiantes
                curso_id = request.POST.get('curso_id')  # ID del curso (asumiendo que viene del formulario)
                curso = Curso.objects.filter(id=curso_id).first()

                if curso and curso.estudiantes.count() >= 4:
                    messages.error(request, 'El curso seleccionado ya tiene el máximo de 4 estudiantes.')
                else:
                    ProfesorJefe.objects.create(
                        nombre=nombre,
                        apellido=apellido,
                        correo=correo,
                        telefono=telefono
                    )
                    messages.success(request, 'Profesor jefe creado exitosamente.')
                    return redirect('gestionar_cursos')
        else:
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')

    return render(request, 'crear_profesor_jefe.html')


from django.db import transaction

def asignar_profesor(request):
    if request.method == 'POST':
        profesor_id = request.POST.get('profesor')
        asignatura_id = request.POST.get('asignatura')
        curso_id = request.POST.get('curso')

        try:
            with transaction.atomic():  # Aseguramos la transacción completa
                profesor = Profesor.objects.get(id=profesor_id)
                asignatura = Asignatura.objects.get(id=asignatura_id)
                curso = Curso.objects.get(id=curso_id)

                # Validar si el profesor ya está asignado a esta asignatura en este curso
                if asignatura in profesor.asignaturas.all() and asignatura in curso.asignaturas.all():
                    messages.warning(request, f"El profesor {profesor.nombre} ya está asignado a la asignatura {asignatura.nombre} en el curso {curso.nombre}.")
                    return redirect('asignar_profesor')

                # Asignar el profesor a la asignatura y curso
                profesor.asignaturas.add(asignatura)
                curso.asignaturas.add(asignatura)

                messages.success(request, f"El profesor {profesor.nombre} fue asignado a la asignatura {asignatura.nombre} del curso {curso.nombre}.")
                return redirect('asignar_profesor')

        except Profesor.DoesNotExist:
            messages.error(request, "El profesor seleccionado no existe.")
        except Asignatura.DoesNotExist:
            messages.error(request, "La asignatura seleccionada no existe.")
        except Curso.DoesNotExist:
            messages.error(request, "El curso seleccionado no existe.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {e}")

    profesores = Profesor.objects.all()
    asignaturas = Asignatura.objects.all()
    cursos = Curso.objects.all()

    return render(request, 'asignar_profesor.html', {
        'profesores': profesores,
        'asignaturas': asignaturas,
        'cursos': cursos,
    })
# View para la asignación de estudiantes
def asignar_estudiante(request):
    if request.method == 'POST':
        estudiantes_ids = request.POST.getlist('estudiantes')
        curso_id = request.POST.get('curso')

        try:
            curso = Curso.objects.get(id=curso_id)
            estudiantes = Estudiante.objects.filter(id__in=estudiantes_ids)

            # Validar si el curso está lleno
            if curso.esta_lleno:
                messages.error(request, f"El curso '{curso.nombre}' ya está lleno. No se pueden asignar más estudiantes.")
                return redirect('asignar_estudiante')

            asignados = 0  # Contador para estudiantes asignados

            for estudiante in estudiantes:
                if not curso.esta_lleno:  # Validar espacio en cada iteración
                    curso.estudiantes.add(estudiante)
                    estudiante.curso = curso  # Actualizar el campo `curso` del estudiante
                    estudiante.save()
                    asignados += 1
                else:
                    messages.warning(request, f"El curso '{curso.nombre}' alcanzó su límite. No todos los estudiantes pudieron ser asignados.")
                    break

            if asignados > 0:
                messages.success(request, f"{asignados} estudiante(s) fueron asignados al curso '{curso.nombre}'.")
            else:
                messages.error(request, f"No se asignaron estudiantes porque el curso '{curso.nombre}' ya estaba lleno.")

            return redirect('asignar_estudiante')

        except Curso.DoesNotExist:
            messages.error(request, "El curso seleccionado no existe.")

    # Filtrar estudiantes sin curso asignado
    estudiantes = Estudiante.objects.filter(curso__isnull=True)
    cursos = Curso.objects.all()

    return render(request, 'asignar_estudiante.html', {
        'estudiantes': estudiantes,
        'cursos': cursos,
    })
    
def gestionar_asignaciones(request):
    return render(request, 'gestionar_asignaciones.html')

def listar_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'listar_cursos.html', {'cursos': cursos})