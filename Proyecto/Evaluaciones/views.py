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
from django.db.models import Count
from django.db.models import Sum

def index(request):
    
    return redirect(reverse('login'))

@login_required
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

@login_required
def dashboard(request):
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
    return render(request, 'dashboard.html', context)

@login_required
def altaEmpleados(request):
    puestos = Puestos.objects.all()
    rangos = Rangos.objects.all()
    departamentos = Departamentos.objects.all()
    empleados = Empleados.objects.filter(estatus=1).latest('no_emp')
    no_empleado= empleados.no_emp + 1
    return render(request, 'altaEmpleados.html', {'formulario': crearEmpleado(), 'puestos': puestos, 'rangos': rangos, 'departamentos': departamentos, 'no_empleado': no_empleado})

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
    valores = {10,20,30,40,50,60,70,80,90,100}
    empp = Empleados.objects.filter(estatus=1)
    context={
        'fecha': fecha,
        'valores': valores
    }

    return render(request, 'crearEvaluacion.html', {'fecha': fecha, 'valores': valores, 'empp': empp})

def crearEvaluacion2(request):
    fecha = Fechas.objects.latest('id')
    #evaluacion = Evaluaciones.objects.latest('id')
    valores = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    empp = Empleados.objects.filter(estatus=1)
    return render(request, 'crearEvaluacion.html', {'fecha': fecha, 'valores': valores})

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
    rutas = Seguimiento.objects.all()
    return render(request, 'rutaEvaluacion.html', {'empleados': empleados, 'rutas': rutas})

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

#para guardar los comentarios y la calificación del objetivo 



#editar evaluación asignada
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

def obtener_datos_evaluaciones_asignada(request):
    if request.method == 'GET' and request.is_ajax():
        seguimiento = request.GET.get('seguimiento_id')
        evaluacion_id = request.GET.get('eva_id')
        empleado_id = request.GET.get('empleado_id')
        fecha_id = request.GET.get('fecha_id')
        numeroEvaluacion = request.GET.get('numeroEvaluacion_id')
        objetivos = Objetivos.objects.filter(numeroEvaluacion_id=numeroEvaluacion)
        
        empleado = Empleados.objects.get(no_emp=empleado_id)   

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


        if bandera == 0:
            evaluacion = Evaluaciones.objects.get(id=evaluacion_id.id)
            evaluacion.seguimiento= seguimiento
            evaluacion.numeroEvaluacion = numeroEvaluacion  
            evaluacion.save()

        data = {
            'bandera': bandera
        }
        return JsonResponse(data)