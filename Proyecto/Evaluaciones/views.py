from django.shortcuts import render, redirect
from .forms import crearEmpleado, EmailAuthenticationForm
from datetime import datetime
from evaluaciones.models import Empleados, Puestos, Rangos, Usuarios, Departamentos, Fechas, Evaluaciones, Objetivos, NumerosEvaluaciones, Apartados, Seguimiento, Fases, ComentariosObjetivos, Comentarios
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
import json
from django.http import JsonResponse
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from .permissions import VerDashboardPermission


def index(request):
    
    return redirect(reverse('login'))

@permission_classes([IsAuthenticated, VerDashboardPermission])
def imagenes(request):
    empleados = Empleados.objects.filter(estatus=1)
    
    # Obtener la cantidad de empleados por departamento y ordenarlos por departamento
    cantidad = Empleados.objects.filter(estatus=1).values('departamento_id').annotate(cantidad=Count('id')).order_by('departamento_id')
    departamentos_con_empleados = [c['departamento_id'] for c in cantidad]
    
    # Filtrar los departamentos que tienen empleados
    departamentos = Departamentos.objects.filter(id__in=departamentos_con_empleados)
    context ={
        'empleados': empleados,
        'departamentos': departamentos,
        'cantidad': cantidad
    }
    return render(request, 'imagenes.html', context)

#Muestra la vista principal del sistema, manda los datos necesarios para que se pueda ver el dashboard
@login_required
def dashboard(request):
    empleados = Empleados.objects.filter(estatus=1)
    #Como es la vista principal del sistema y la que se muestra cada que se inicia sesión
    #Se hace una validación para que cada mes se cree una nueva fecha y se creen las evaluaciones correspondientes
    #Se crean todas las evaluaciones del mes anterior pero con la fecha actual
    fechaActual = datetime.now()
    print (fechaActual)
    fecha = Fechas.objects.latest('id')
    print(fecha)
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    print(dia)
    print(mes)
    print(año)

    #para hacerlo cada mes solo cambiar la variable dia por mes, esto solo es de practica
    if (dia != fecha.mes or año != fecha.anio):
        fechaAnterior = Fechas.objects.latest('id')
        fecha = Fechas(
            mes = dia,
            anio = año,
            version = fecha.version + 1
        )
        fecha.save()
        evaluacionesAnteriores = Evaluaciones.objects.filter(fecha_id=fechaAnterior.id)
        fechaNueva = Fechas.objects.latest('id')
        for evaluacion in evaluacionesAnteriores:
            ev = Evaluaciones (
                fecha_id = fechaNueva.id,
                empleado_id = evaluacion.empleado_id,
                estatus = 0,
                numeroEvaluacion_id = evaluacion.numeroEvaluacion_id,
                seguimiento_id = evaluacion.seguimiento_id,
                fechaActivacion = evaluacion.fechaActivacion,
                fase_id = 1
            )
            ev.save()

            eva = Evaluaciones.objects.latest('id')

            comentarios = Comentarios(
                evaluacion_id=eva.id,
                comentario_autoevaluado="",
                comentario_evaluador1="",
                comentario_evaluador2="",
                comentario_evaluador3="",
                comentario_evaluador4="",
                comentario_capitalHumano="",
                comentario_director="",
                logros="",
                estatus=1
            )
            
            comentarios.save()
        

    # Obtener la cantidad de empleados por departamento y ordenarlos por departamento
    cantidad = Empleados.objects.filter(estatus=1).values('departamento_id').annotate(cantidad=Count('id')).order_by('departamento_id')
    departamentos_con_empleados = [c['departamento_id'] for c in cantidad]

    ultimaFecha = Fechas.objects.latest('id')
    evaluaciones = Evaluaciones.objects.filter(Q(estatus__in=[0,1]) & Q(fase_id__in=[1,2]) & Q(fecha_id=ultimaFecha.id)).select_related('fecha', 'empleado', 'numeroEvaluacion', 'seguimiento', 'fase')
    # Filtrar los departamentos que tienen empleados3
    departamentos = Departamentos.objects.filter(id__in=departamentos_con_empleados)

    context ={
        'empleados': empleados,
        'departamentos': departamentos,
        'cantidad': cantidad,
        'evaluaciones': evaluaciones
    }
    return render(request, 'dashboard.html', context)

#Muestra la vista para crear empleados
#Manda los datos necesarios para que se pueda crear un empleado
@login_required
def altaEmpleados(request):
    puestos = Puestos.objects.all()
    rangos = Rangos.objects.all()
    departamentos = Departamentos.objects.all()
    empleados = Empleados.objects.filter(estatus=1).latest('no_emp')
    no_empleado= empleados.no_emp + 1
    return render(request, 'altaEmpleados.html', {'formulario': crearEmpleado(), 'puestos': puestos, 'rangos': rangos, 'departamentos': departamentos, 'no_empleado': no_empleado})


#Muestra la vista donde esta esta la tabla con todos los empleados
@login_required
def listaEmpleados(request):
    empleados = Empleados.objects.filter(estatus=1)
    return render(request, 'listaEmpleados.html', {'empleados': empleados})


# Función para iniciar sesión
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': EmailAuthenticationForm()})
    else:
        print(request.POST)
        return render(request, 'login.html',{'form', EmailAuthenticationForm()})

# Función para cerrar sesión
@login_required  
def salir(request):
    logout(request)
    return redirect('/')

#no la ocupo creo
@login_required
def verEmpleados(request):
    empleados = Empleados.objects.filter(estatus=1)
    return render(request, 'listaEmpleados.html', {'empleados': empleados})


#Muestra principal de las evaluaciones, manda a la vista de evaluaciones.html
#Es donde se muestran de manera general las evaluaciones que se han asignado a los empleados
@login_required
def evaluaciones(request):
    empleados = Empleados.objects.filter(estatus=1)
    empleados = Empleados.objects.filter(estatus=1)
    fases = Fases.objects.all()
    evaluaciones = Evaluaciones.objects.all().select_related('fecha', 'empleado', 'numeroEvaluacion', 'seguimiento', 'fase')
    fechas = Fechas.objects.latest('id')
    seguimientos = Seguimiento.objects.all()

    return render(request, 'evaluaciones.html', {'empleados': empleados, 'fases': fases, 'evaluaciones': evaluaciones, 'fechas': fechas , 'seguimientos': seguimientos})


#No lo ocupo hasta el momento
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
    
    
#Creo que no lo ocupo y ocupo el de abajo
def crearEvaluacion(request):
    fecha = Fechas.objects.latest('id')
    valores = {10,20,30,40,50,60,70,80,90,100}
    empp = Empleados.objects.filter(estatus=1)
    context={
        'fecha': fecha,
        'valores': valores
    }

    return render(request, 'crearEvaluacion.html', {'fecha': fecha, 'valores': valores, 'empp': empp})

#Muestra la vista para crear una evaluacion
def crearEvaluacion2(request):
    fecha = Fechas.objects.latest('id')
    #evaluacion = Evaluaciones.objects.latest('id')
    valores = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    empp = Empleados.objects.filter(estatus=1)
    return render(request, 'crearEvaluacion.html', {'fecha': fecha, 'valores': valores})


#Muestra la vista para asignar una evaluacion a un empleado
#Se mandan todos los datos necesarios para que se pueda asignar una evaluacion
#Se manda la información de la última evaluación para que se pueda ver en lo que escoge el combo
@login_required
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

    sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
    sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
    sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()

    context = {
        'fecha': fecha,
        'empleados': empleados,
        'numeroEvaluacion': numeroEvaluacion,
        'objetivos': objetivos,
        'apartados': apartados,
        'seguimientos': seguimientos,
        'rut': rut,
        'obj': obj,
        'eva': eva,
        'sumOKR': sumOKR,
        'sumKPI': sumKPI,
        'sumCL': sumCL
    }
    return render(request, 'asignarEvaluacion.html',context)


# Lo ocupo en asignarEvaluacion.html y editarEvaluacion.html para que se muestren los objetivos de acuerdo al id de la evaluacion seleccionada
def obtener_datos_evaluacion(request):
    if request.method == 'GET' and request.is_ajax():
        evaluacion_id = request.GET.get('evaluacion_id')
        # Convierte el ID de la evaluación a entero
        evaluacion_id = int(evaluacion_id)

        datos_OKR = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=1) 
        datos_KPI = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=2)
        datos_CL = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=3)
        datos_BONO  = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=4)
        datos_RESULTADOS = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=5)

        sumaOKR = datos_OKR.aggregate(total_okr=Sum('valor'))['total_okr']
        sumaKPI = datos_KPI.aggregate(total_kpi=Sum('valor'))['total_kpi']
        sumaCL = datos_CL.values_list('valor', flat=True).first()

        data = {
            'OKR': list(datos_OKR.values()),
            'KPI': list(datos_KPI.values()),
            'CL': list(datos_CL.values()),
            'BONO': list(datos_BONO.values()),
            'RESULTADOS': list(datos_RESULTADOS.values()),
            'sumaOKR': sumaOKR,
            'sumaKPI': sumaKPI,
            'sumaCL': sumaCL
        }
        return JsonResponse(data)


#Este creo que ya no lo ocupo
#Es para guardar los objetivos separados en apartados en la base de datos
#Creo que ya no se ocupa por que me dio error en el servidor y lo cambie por el que esta abajo  
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


#Guarda la evaluacion que se a creado en la vista de crearEvaluacion.html y en editarEvaluacion.html
#Se reciben diferentes arreglos con los datos de los objetivos separados cada uno por apartado
#Se crea una nueva evaluacion y a esa se le asignan los objetivos

def guardarEvaluacionBD(request):
    if request.method == 'POST':
        try:
            # Obtener los datos de los arreglos desde el formulario
            arregloBonos_str = request.POST.get('arregloBonos')
            arregloCLs_str = request.POST.get('arregloCLs')
            arregloKPIs_str = request.POST.get('arregloKPIs')
            arregloOKRs_str = request.POST.get('arregloOKRs')
            arregloResultados_str = request.POST.get('arregloResultados')

            # Convertir las cadenas JSON a diccionarios
            arregloBonos = json.loads(arregloBonos_str)
            arregloCLs = json.loads(arregloCLs_str)
            arregloKPIs = json.loads(arregloKPIs_str)
            arregloOKRs = json.loads(arregloOKRs_str)
            arregloResultados = json.loads(arregloResultados_str)

            print("Arreglo Bonos:", arregloBonos)
            print("Arreglo CLs:", arregloCLs)
            print("Arreglo KPIs:", arregloKPIs)
            print("Arreglo OKRs:", arregloOKRs)
            print("Arreglo Resultados:", arregloResultados)

            evaluacion = NumerosEvaluaciones(
            estatus=1,
            fechaCreacion=datetime.now()
            )
            evaluacion.save()

            numeroEvaluacion = NumerosEvaluaciones.objects.latest('id')

            # Ahora puedes iterar sobre los arreglos y acceder a los datos
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

            for item in arregloResultados:
                objetivo = Objetivos(
                     objetivo=item['objetivo'],
                    metrica=item['metrica'],
                    valor=item['valor'],
                    estatus=1,
                    apartado_id=5,
                    numeroEvaluacion_id=numeroEvaluacion.id
                )
                objetivo.save()


            return redirect(reverse('evaluaciones'))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Esta vista solo acepta solicitudes POST.'}, status=405)


#Se recibe un id del empleado que se quiere editar y se manda a la vista de editarEmpleado.html
@login_required
def editarEmpleado(request, id):
    empleado = Empleados.objects.get(no_emp=id)
    puestos = Puestos.objects.all()
    rangos = Rangos.objects.all()
    departamentos= Departamentos.objects.all()
    return render(request, 'editarEmpleado.html', {'empleado': empleado, 'puestos': puestos, 'rangos': rangos, 'departamentos': departamentos})


#Edita un empleado de la base de datos en las tablas de empleados y usuarios(usuarios de django)
# De acuerdo con los cambios de la vista de editarEmpleado.html
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

#Elimina un empleado de la base de datos de manera lógica ya que solo cambia su estatus a 0
#Se recibe el id del empleado que se quiere eliminar  
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

#Guarda un empleado en la base de datos en la tabla de empleados y en la tabla de usuarios(usuarios de django)
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

#Muestra la vista para crear las rutas de evaluacion y aquellas rutas de evaluacion existentes
@login_required
def rutaEvaluacion(request):
    empleados = Empleados.objects.filter(estatus=1)
    rutas = Seguimiento.objects.all()
    return render(request, 'rutaEvaluacion.html', {'empleados': empleados, 'rutas': rutas})


#Guarda la ruta de evaluacion que se a escogido en la vista de rutaEvaluacion.html y redirige a la vista de evaluaciones
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

#Lo ocupo para vista de asignarEvaluacion.html que se puedan ver los evaluadores de cada seguimiento de acuerdo al id seleccionado
@login_required
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
    
#la ocupo en la vista de asignarEvaluacion.html antes de que se guarde la evaluacion
# para que no se pueda asignar una evaluacion a un empleado si ya tiene una evaluacion asignada para el mismo mes
# o para que no se le asigne una evaluación no válida al empleado
@login_required
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

        for objetivo in objetivos:
            if objetivo.apartado_id == 4 and empleado.departamento_id not in [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]:
                bandera = 2
                if (empleado.rango_id != 4):
                    print("El rango del empleado es diferente de 4")
                    bandera = 3
                    print("Bandera ahora es:", bandera)
        data = {
            'bandera': bandera
        }
        return JsonResponse(data)
    



#Cuando se asigna una evaluacion a un empleado aqui se guarda la información, es para llenar la tabla de evaluaciones
def guardarEvaluacionMensual (request):
    empleado_id = int(request.POST['empleado'])
    numeroEvaluacion_id = int(request.POST['numeroEvaluacion'])
    seguimiento_id = int(request.POST['seguimiento'])
    fecha = Fechas.objects.latest('id')
    fechaActivacion = datetime.now()
    estatus = 0

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

    eva = Evaluaciones.objects.latest('id')

    comentarios = Comentarios(
        evaluacion_id=eva.id,
        comentario_autoevaluado="",
        comentario_evaluador1="",
        comentario_evaluador2="",
        comentario_evaluador3="",
        comentario_evaluador4="",
        comentario_capitalHumano="",
        comentario_director="",
        logros="",
        estatus=1
    )

    comentarios.save()

    return redirect(reverse('evaluaciones'))


#guarda evaluacion que a sido editada de un empleado para un mes
def guardarEvaluacionEditada (request):
    #empleado_id = int(request.POST['empleado'])
    evaluacion = int(request.POST['eva'])
    numeroEvaluacion_id = int(request.POST['numeroEvaluacion'])
    seguimiento_id = int(request.POST['seguimiento'])
    #fecha = Fechas.objects.latest('id')

    evaluacion = Evaluaciones.objects.get(id=evaluacion)
    evaluacion.seguimiento_id= seguimiento_id
    evaluacion.numeroEvaluacion_id = numeroEvaluacion_id  
    evaluacion.save()
    evaluacion.save()
    return redirect(reverse('evaluaciones'))


@login_required
def obtener_datos_evaluaciones_editada(request):
    if request.method == 'GET' and request.is_ajax():
        empleado_id = request.GET.get('empleado_id')
        fecha_id = request.GET.get('fecha_id')
        numeroEvaluacion = request.GET.get('numeroEvaluacion_id')
        empleado = Empleados.objects.get(no_emp=empleado_id)    
        evaluaciones = Evaluaciones.objects.filter(empleado_id=empleado_id)
        objetivos = Objetivos.objects.filter(numeroEvaluacion_id=numeroEvaluacion)

        bandera = 0

        for objetivo in objetivos:
            if objetivo.apartado_id == 4 and empleado.departamento_id not in [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]:
                bandera = 2
                if (empleado.rango_id != 4):
                    print("El rango del empleado es diferente de 4")
                    bandera = 3
                    print("Bandera ahora es:", bandera)
        data = {
            'bandera': bandera
        }
        return JsonResponse(data)


#muestra la vista para crear una evaluacion en base a una existente
def editarEvaluacion(request):
    numeroEvaluacion=NumerosEvaluaciones.objects.all()
    eva = NumerosEvaluaciones.objects.latest('id')
    obj = Objetivos.objects.filter(numeroEvaluacion_id = eva.id)
    valores = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
    sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
    sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()

    context = {
        'numeroEvaluacion': numeroEvaluacion,
        'obj': obj,
        'valores': valores,
        'eva': eva,
        'sumOKR': sumOKR,
        'sumKPI': sumKPI,
        'sumCL': sumCL
    }
    return render(request, 'editarEvaluacion.html',context)


#funcion para mandar la información necesaria para contestar la autoevaluación
#esta no la estoy ocupando hasta el momento
def evaluacionUsuario (request):
    empleado=Empleados.objects.get(no_emp=request.user.no_emp)
    fecha = Fechas.objects.latest('id')
    evaluacion = Evaluaciones.objects.filter(empleado_id=empleado.no_emp, fecha_id=fecha.id)
    objetivos = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id)
    seguimiento = Seguimiento.objects.filter(id=evaluacion.seguimiento_id)
    context ={ 
        "evaluacion": evaluacion,
        "objetivos": objetivos,
        "seguimiento": seguimiento
    }
    return render(request, 'evaluacionUsuario.html', {'evaluaciones': evaluaciones})




#Muestra la vista para editar la evaluación asignada, le manda toda la info de la evaluacion para que se pueda ver en lo que escoge el combo
def editarEvaluacionAsignada(request,id):
    idd = id
    fecha = Fechas.objects.latest('id')
    empleados = Empleados.objects.filter(estatus=1)
    numeroEvaluacion = NumerosEvaluaciones.objects.all()
    objetivos=Objetivos.objects.all()
    apartados = Apartados.objects.all()
    seguimientos = Seguimiento.objects.all()
    
    eva = Evaluaciones.objects.get(id=idd)
    numEva= NumerosEvaluaciones.objects.get(id=eva.numeroEvaluacion_id)
    obj = Objetivos.objects.filter(numeroEvaluacion_id=eva.numeroEvaluacion_id)
    emp = Empleados.objects.get(no_emp= eva.empleado_id)
    rut = Seguimiento.objects.get(id=eva.seguimiento_id)
    
    sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
    sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
    sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()

    context = {
        'fecha': fecha,
        'empleados': empleados,
        'numeroEvaluacion': numeroEvaluacion,
        'objetivos': objetivos,
        'apartados': apartados,
        'seguimientos': seguimientos,
        'rut': rut,
        'obj': obj,
        'sumOKR': sumOKR,
        'sumKPI': sumKPI,
        'sumCL': sumCL,
        'emp': emp,
        'numEva': numEva,
        'eva': eva,

    }
    return render(request, 'editarEvaluacionAsignada.html', context)


#Muestra la vista de comentarios iniciales, donde pueden comentar los evaluadores 1 y los de capital humano a todos
@login_required
def comentariosInicio (request):
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleado= Empleados.objects.get(no_emp=no_emp)

    #checar donde el seguimiento sea igual al empleado logueado y si es evaluador 1 significa que puede poner comentarios, esa consulta me va a regresar varios
    #por que puede que el evaluador este varias veces en la tabla de seguimiento como evaluasor 1

    if (empleado.departamento_id == 11 or empleado.no_emp == 283 or empleado.no_emp==101):
        fecha = Fechas.objects.latest('id')
        evaSegui = Evaluaciones.objects.filter(fecha_id=fecha.id)
    else:
        try:
            seguimientos = Seguimiento.objects.filter(evaluador1_id=empleado.no_emp)
            evaSegui = []
            for segui in seguimientos:
                fecha = Fechas.objects.latest('id')
                evaluaciones = Evaluaciones.objects.filter(seguimiento_id=segui.id, estatus=0, fecha_id=fecha.id)
                evaSegui.extend(evaluaciones)
        except:
            evaSegui = []
    context ={
        "evaSegui": evaSegui,
        "empleado": empleado,
    }

    return render(request, 'comentariosInicio.html', context)


#Guarda los comentarios iniciales de acuerdo a lo que se escriba en comentariosInicio.html
#se podría ocupar para guardar los comentarios de todos
def guardar_comentarios_iniciales(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('comentarios'))
        comentariosGenerales = json.loads(request.POST.get('comentariosGenerales'))

        print(data)
        print(comentariosGenerales)
        numEva = request.POST.get('numeroEvaluacion')
        evaluacion = Evaluaciones.objects.get(id=numEva)
        print(evaluacion.id)
        usuario=1
        if request.user.is_authenticated:
            usuario= request.user.id
        print(usuario)
        usuario= Usuarios.objects.get(id=usuario)   
        empleado = Empleados.objects.get(no_emp=usuario.no_emp)  
        print(empleado) 
        no_emp = empleado.no_emp

        for item in data:
            print(item)
            print (item['comentario'])
            print (item['id'])
            comentariosObjetivos = ComentariosObjetivos(
                comentario= item['comentario'],
                objetivo_id= item['id'],
                fechaComentario = datetime.now(),
                fecha_id = evaluacion.fecha_id,
                evaluacion_id = evaluacion.id,
                quienComenta_id = no_emp,
                estatus=1,
            )
            comentariosObjetivos.save()
        
        if empleado.departamento_id != 11:
            evaluacion.estatus = 1
            evaluacion.fase_id = 2
            evaluacion.save()

        if len(comentariosGenerales) != 0:
            comentarios = Comentarios.objects.get(evaluacion_id=evaluacion.id)
            if empleado.departamento_id == 11:
                nuevo_comentario = comentarios.comentario_capitalHumano + " -> " + comentariosGenerales[0]['comentario']
                comentarios.comentario_capitalHumano = nuevo_comentario.strip()  # Elimina posibles espacios en blanco al inicio y al final
            else:
                comentarios.comentario_evaluador1 = comentariosGenerales[0]['comentario']
            comentarios.save()

        return JsonResponse({'message': 'Comentarios guardados exitosamente'})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)


#Mostrar la vista de la autoevaluación y sus comentarios
def autoevaluacion (request):
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleado= Empleados.objects.get(no_emp=no_emp)
    fecha = Fechas.objects.latest('id')

    siHayBono = False
    siHayResultados = False
    
    try: 
        # AQUI TENGO QUE VALIDAR QUE LA EVALUACION ESTE EN LA FASE 2 PARA QUE DESPUES DE CONTESTADA YA NO SE PUEDA CONTESTAR
        evaluacion= Evaluaciones.objects.filter(empleado_id=empleado.no_emp, fecha_id=fecha.id)
        print(evaluacion[0].id)
        comentariosGenerales = Comentarios.objects.get(evaluacion_id=evaluacion[0].id)
        obj = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion[0].numeroEvaluacion_id)
        obj= Objetivos.objects.filter(numeroEvaluacion_id=evaluacion[0].numeroEvaluacion_id).prefetch_related('comentariosobjetivos_set')

        sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
        sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
        sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()

        for o in obj:
            if o.apartado_id == 4:
                siHayBono = True
            if o.apartado_id == 5:
                siHayResultados = True
    except:
        evaluacion = []
        obj = []
        comentariosGenerales = []
        sumOKR = []
        sumKPI = []
        sumCL = []


    context ={
        "evaluacion": evaluacion,
        "obj": obj,
        "empleado": empleado,
        "sumOKR": sumOKR,
        "sumKPI": sumKPI,
        "sumCL": sumCL,
        "siHayBono": siHayBono,
        "siHayResultados": siHayResultados,
        "comentariosGenerales": comentariosGenerales
    }
    return render(request, 'autoevaluacion.html', context)


def traerDatosEmpleado(request):
    if request.method == 'GET' and request.is_ajax():
        no_emp = request.GET.get('no_emp')
        empleado = Empleados.objects.get(no_emp=no_emp)

        empleado_dict = {
            'nombre': empleado.nombre,
            'apellido_paterno': empleado.apellido_paterno,
            'apellido_materno': empleado.apellido_materno,
            'correo': empleado.correo,
            'puesto': empleado.puesto_id,
            'rango': empleado.rango_id,
            'departamento': empleado.departamento_id,
            'estatus': empleado.estatus,
            'no_emp': empleado.no_emp,
            'password': empleado.password,
        }

        data = {
            'empleado': empleado_dict

        }
        return JsonResponse(data)


def obtener_datos_evaluacion_comentarios(request):
    if request.method == 'GET' and request.is_ajax():
        evaluacion_id = request.GET.get('evaluacion_id')
        # Convierte el ID de la evaluación a entero
        evaluacion_id = int(evaluacion_id)
        evaluacion= Evaluaciones.objects.get(id=evaluacion_id)
        evaluacion_id = evaluacion.numeroEvaluacion_id


        datos_OKR = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=1).prefetch_related('comentariosobjetivos_set')
        datos_KPI = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=2).prefetch_related('comentariosobjetivos_set')
        datos_CL = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=3).prefetch_related('comentariosobjetivos_set')
        datos_BONO = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=4).prefetch_related('comentariosobjetivos_set')
        datos_RESULTADOS = Objetivos.objects.filter(numeroEvaluacion=evaluacion_id, estatus=1, apartado_id=5).prefetch_related('comentariosobjetivos_set')
        

        coment_OKR = ComentariosObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=1).select_related('objetivo','quienComenta_id')
        coment_KPI = ComentariosObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=2).select_related('objetivo','quienComenta_id')
        coment_CL = ComentariosObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=3).select_related('objetivo','quienComenta_id')
        coment_BONO = ComentariosObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=4).select_related('objetivo','quienComenta_id')
        coment_RESULTADOS = ComentariosObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=5).select_related('objetivo','quienComenta_id')

        empleados = Empleados.objects.filter(estatus=1)

        sumaOKR = datos_OKR.aggregate(total_okr=Sum('valor'))['total_okr']
        sumaKPI = datos_KPI.aggregate(total_kpi=Sum('valor'))['total_kpi']
        sumaCL = datos_CL.values_list('valor', flat=True).first()

        data = {
            'OKR': list(datos_OKR.values()),
            'KPI': list(datos_KPI.values()),
            'CL': list(datos_CL.values()),
            'BONO': list(datos_BONO.values()),
            'RESULTADOS': list(datos_RESULTADOS.values()),
            'sumaOKR': sumaOKR,
            'sumaKPI': sumaKPI,
            'sumaCL': sumaCL,
            'coment_OKR': list(coment_OKR.values()),
            'coment_KPI': list(coment_KPI.values()),
            'coment_CL': list(coment_CL.values()),
            'coment_BONO': list(coment_BONO.values()),
            'coment_RESULTADOS': list(coment_RESULTADOS.values()),
            'empleados': list(empleados.values())

        }
        return JsonResponse(data)
    
def calendario (request):
    return render(request, 'calendario.html')
