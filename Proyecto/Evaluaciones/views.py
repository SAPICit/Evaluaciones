from django.shortcuts import render, redirect
from .forms import crearEmpleado, EmailAuthenticationForm
from datetime import datetime
from evaluaciones.models import Empleados, Puestos, Rangos, Usuarios, Departamentos, Fechas, Evaluaciones, Objetivos, NumerosEvaluaciones, Apartados, Seguimiento, Fases
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
import json
from django.http import JsonResponse


def index(request):
    return redirect(reverse('login'))

@login_required
def imagenes(request):
    return render(request, 'imagenes.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def altaEmpleados(request):
    puestos = Puestos.objects.all()
    rangos = Rangos.objects.all()
    departamentos = Departamentos.objects.all()
    return render(request, 'altaEmpleados.html', {'formulario': crearEmpleado(), 'puestos': puestos, 'rangos': rangos, 'departamentos': departamentos})

@login_required
def listaEmpleados(request):
    empleados = Empleados.objects.filter(estatus=1)
    return render(request, 'listaEmpleados.html', {'empleados': empleados})

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': EmailAuthenticationForm()})
    else:
        print(request.POST)
        return render(request, 'login.html',{'form', EmailAuthenticationForm()})

@login_required  
def salir(request):
    logout(request)
    return redirect('/')

@login_required
def verEmpleados(request):
    empleados = Empleados.objects.filter(estatus=1)
    return render(request, 'listaEmpleados.html', {'empleados': empleados})

def evaluaciones(request):
    empleados = Empleados.objects.filter(estatus=1)
    empleados = Empleados.objects.filter(estatus=1)
    fases = Fases.objects.all()
    evaluaciones = Evaluaciones.objects.all().select_related('fecha', 'empleado', 'numeroEvaluacion', 'seguimiento', 'fase')
    fechas = Fechas.objects.latest('id')
    seguimientos = Seguimiento.objects.all()

    return render(request, 'evaluaciones.html', {'empleados': empleados, 'fases': fases, 'evaluaciones': evaluaciones, 'fechas': fechas , 'seguimientos': seguimientos})

def fechaMes (request, fecha):
    if (fecha == 1):
        return "Enero" + fecha.anio
    elif (fecha == 2):
        return "Febrero" + fecha.anio
    elif (fecha == 3):
        return "Marzo"  + fecha.anio
    elif (fecha == 4):
        return "Abril"  + fecha.anio
    elif (fecha == 5):
        return "Mayo"   + fecha.anio
    elif (fecha == 6):
        return "Junio"  + fecha.anio
    elif (fecha == 7):
        return "Julio"  + fecha.anio
    elif (fecha == 8):
        return "Agosto" + fecha.anio
    elif (fecha == 9):
        return "Septiembre" + fecha.anio
    elif (fecha == 10):
        return "Octubre" + fecha.anio
    elif (fecha == 11):
        return "Noviembre" + fecha.anio
    elif (fecha == 12):
        return "Diciembre" + fecha.anio
    
    

def crearEvaluacion(request):
    fecha = Fechas.objects.latest('id')
    return render(request, 'crearEvaluacion.html', {'fecha': fecha})

def crearEvaluacion2(request):
    fecha = Fechas.objects.latest('id')
    #evaluacion = Evaluaciones.objects.latest('id')
    return render(request, 'crearEvaluacion.html', {'fecha': fecha})

def asignarEvaluacion(request):
    fecha = Fechas.objects.latest('id')
    empleados = Empleados.objects.filter(estatus=1)
    numeroEvaluacion = NumerosEvaluaciones.objects.all()
    objetivos=Objetivos.objects.all()
    apartados = Apartados.objects.all()
    seguimientos = Seguimiento.objects.all()
    rut = Seguimiento.objects.latest('id')
    eva = NumerosEvaluaciones.objects.latest('id')
    obj = Objetivos.objects.filter(numeroEvaluacion_id = eva.id)
    return render(request, 'asignarEvaluacion.html', {'fecha': fecha, 'empleados': empleados, 'numeroEvaluacion': numeroEvaluacion, 'objetivos': objetivos, 'apartados': apartados, 'seguimientos': seguimientos, 'rut': rut,'obj': obj})



def obtener_datos_evaluacion(request):
    if request.method == 'GET' and request.is_ajax():
        evaluacion_id = request.GET.get('evaluacion_id')
        # Convierte el ID de la evaluación a entero
        evaluacion_id = int(evaluacion_id)

        datos_OKR = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=1) 
        datos_KPI = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=2)
        datos_CL = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=3)
        datos_BONO  = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=4)

        data = {
            'OKR': list(datos_OKR.values()),
            'KPI': list(datos_KPI.values()),
            'CL': list(datos_CL.values()),
            'BONO': list(datos_BONO.values()),
        }
        return JsonResponse(data)


    
def crearEvaluacionDB(request, arregloBonos, arregloCLs, arregloKPIs, arregloOKRs):
    arregloBonos = json.loads(arregloBonos)
    arregloCLs = json.loads(arregloCLs)
    arregloKPIs = json.loads(arregloKPIs)
    arregloOKRs = json.loads(arregloOKRs)
    eva=0
    numeroEvaluacionPr = NumerosEvaluaciones.objects.latest('id')


    evaluacion = NumerosEvaluaciones(
        estatus=1,
        fechaCreacion=datetime.now()
    )
    evaluacion.save()

    numeroEvaluacion = NumerosEvaluaciones.objects.latest('id')

    # Ahora puedes iterar sobre los arreglos y acceder a los datos
    for item in arregloBonos:
        objetivo = Objetivos(
              objetivo=item['objetivo'],
              metrica=item['metrica'],
              valor=item['valor'],
              estatus=1,
              apartado_id=4,
              numeroEvaluacion_id=numeroEvaluacion.id
         )
        objetivo.save()

    for item in arregloCLs:
        objetivo = Objetivos(
              objetivo=item['objetivo'],
              metrica=item['metrica'],
              valor=item['valor'],
              estatus=1,
              apartado_id=3,
              numeroEvaluacion_id=numeroEvaluacion.id
         )
        objetivo.save()

    for item in arregloKPIs:
        objetivo = Objetivos(
              objetivo=item['objetivo'],
              metrica=item['metrica'],
              valor=item['valor'],
              estatus=1,
              apartado_id=2,
              numeroEvaluacion_id=numeroEvaluacion.id
         )
        objetivo.save()
    
    for item in arregloOKRs:
        objetivo = Objetivos(
              objetivo=item['objetivo'],
              metrica=item['metrica'],
              valor=item['valor'],
              estatus=1,
              apartado_id=1,
              numeroEvaluacion_id=numeroEvaluacion.id
         )
        objetivo.save()


    return redirect(reverse('evaluaciones'))

@login_required
def editarEmpleado(request, id):
    empleado = Empleados.objects.get(no_emp=id)
    puestos = Puestos.objects.all()
    rangos = Rangos.objects.all()
    departamentos= Departamentos.objects.all()
    return render(request, 'editarEmpleado.html', {'empleado': empleado, 'puestos': puestos, 'rangos': rangos, 'departamentos': departamentos})

@login_required
def guardar(request):
    id = int(request.POST['id'])
    no_emp = int (request.POST['no_emp'])
    nombre = request.POST['nombre']
    apellido_paterno = request.POST['apellido_paterno']
    apellido_materno = request.POST['apellido_materno']
    correo = request.POST['correo']
    password = request.POST['password']
    estatus = request.POST['estatus']
    puesto_id = int(request.POST['puesto'])
    rango_id = int(request.POST['rango'])
    departamento_id = int(request.POST['departamento'])

    empleado = Empleados.objects.get(no_emp=no_emp)
    empleado.nombre = nombre
    empleado.apellido_paterno = apellido_paterno
    empleado.apellido_materno = apellido_materno
    empleado.password = password
    empleado.estatus = estatus
    empleado.puesto_id = puesto_id
    empleado.rango_id = rango_id
    empleado.departamento_id = departamento_id


    usuario = Usuarios.objects.get(no_emp=no_emp)
    usuario.last_name = apellido_paterno
    usuario.username =  no_emp
    usuario.first_name = nombre
    usuario.email = correo
    usuario.password = make_password(password)

    
    empleado.save()
    usuario.save()
    empleados = Empleados.objects.filter(estatus=1)
    return redirect(reverse('listaEmpleados'))
            
@login_required
def eliminarEmpleado(request,id):
    emp = Empleados.objects.get(no_emp=id)
    empleado = Empleados.objects.get(no_emp=id)
    empleado.estatus = 0
    empleado.save()
    empleados = Empleados.objects.filter(estatus=1)

    usuario = Usuarios.objects.get(no_emp=emp.no_emp)
    usuario.is_active = 0
    empleado.save()

    return redirect(reverse('listaEmpleados'))


@login_required
def guardarEmpleado(request):
    empleados = Empleados.objects.filter(estatus=1)
    no_emp = int (request.POST['no_emp'])
    nombre = request.POST['nombre']
    apellido_paterno = request.POST['apellido_paterno']
    apellido_materno = request.POST['apellido_materno']
    correo = request.POST['correo']
    password = request.POST['password']
    estatus = request.POST['estatus']
    puesto_id = int(request.POST['puesto'])
    rango_id = int(request.POST['rango'])
    departamento_id = int(request.POST['departamento'])

    usuario = Usuarios.objects.create_user(username=no_emp, email=correo, password=password, first_name=nombre, last_name=apellido_paterno, no_emp=no_emp)

    empleado = Empleados(
        no_emp=no_emp,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        correo=correo,
        password=password,
        puesto_id=puesto_id,
        rango_id=rango_id,
        departamento_id=departamento_id,
        estatus=estatus
    )
    empleado.save()
    usuario.save()
    return redirect(reverse('listaEmpleados'))


@login_required
def rutaEvaluacion(request):
    empleados = Empleados.objects.filter(estatus=1)
    return render(request, 'rutaEvaluacion.html', {'empleados': empleados})

@login_required
def guardarRutaEvaluacion(request):
    evaluador1 = int(request.POST['evaluador1'])
    evaluador2 = int(request.POST['evaluador2'])
    evaluador3 = int(request.POST['evaluador3'])
    evaluador4 = int(request.POST['evaluador4'])

    seguimiento = Seguimiento(
        evaluador1_id=evaluador1,
        evaluador2_id=evaluador2,
        evaluador3_id=evaluador3,
        evaluador4_id=evaluador4,
        estatus = 1
    )
    seguimiento.save()

    return redirect(reverse('evaluaciones'))

def obtener_datos_seguimiento(request):
    if request.method == 'GET' and request.is_ajax():
        evaluacion_id = request.GET.get('seguimiento_id')

        evaluacion_id = int(evaluacion_id)

        seguimiento = Seguimiento.objects.filter(id=evaluacion_id, estatus=1).select_related('evaluador1', 'evaluador2', 'evaluador3', 'evaluador4')
        empleados = Empleados.objects.filter(estatus=1)

        data = {
            'seguimiento': list(seguimiento.values()),  
            'empleados': list(empleados.values())   
        }


        return JsonResponse(data)
    
    
def obtener_datos_evaluaciones(request):
    if request.method == 'GET' and request.is_ajax():
        empleado_id = request.GET.get('empleado_id')
        fecha_id = request.GET.get('fecha_id')
        numeroEvaluacion = request.GET.get('numeroEvaluacion_id')
        empleado = Empleados.objects.get(no_emp=empleado_id)    
        evaluaciones = Evaluaciones.objects.filter(empleado_id=empleado_id)
        objetivos = Objetivos.objects.filter(numeroEvaluacion_id=numeroEvaluacion)


        bandera = 0
        if evaluaciones.exists():
            for evaluacion in evaluaciones:
                if evaluacion.fecha_id != fecha_id:
                    bandera = 1
                break

        for objetivo in objetivos:
            if objetivo.apartado_id == 4 & empleado.rango_id != 4 & (empleado.departamento_id != 14 |  empleado.departamento_id != 15 |  empleado.departamento_id != 16 |  empleado.departamento_id != 17 |  empleado.departamento_id != 18 |  empleado.departamento_id != 19 |  empleado.departamento_id != 20 | empleado.departamento_id != 21 |  empleado.departamento_id != 22 |  empleado.departamento_id != 23 | empleado.departamento_id != 24):
                bandera = 2
                break

        data = {
            'bandera': bandera
        }
        return JsonResponse(data)
    

    
def guardarEvaluacionMensual (request):
    empleado_id = int(request.POST['empleado'])
    numeroEvaluacion_id = int(request.POST['numeroEvaluacion'])
    seguimiento_id = int(request.POST['seguimiento'])
    fecha = Fechas.objects.latest('id')
    fechaActivacion = datetime.now()
    estatus = 1

    evaluacion = Evaluaciones(
        fecha_id=fecha.id,
        empleado_id=empleado_id,
        numeroEvaluacion_id=numeroEvaluacion_id,
        seguimiento_id=seguimiento_id,
        fechaActivacion=fechaActivacion,
        estatus=estatus,
        fase_id=1
    )
    evaluacion.save()
    return redirect(reverse('evaluaciones'))

def editarEvaluacion(request):
    numeroEvaluacion=NumerosEvaluaciones.objects.all()
    return render(request, 'editarEvaluacion.html',{'numeroEvaluacion': numeroEvaluacion})