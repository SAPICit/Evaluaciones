from django.shortcuts import render, redirect
from .forms import crearEmpleado, EmailAuthenticationForm
from datetime import datetime
from evaluaciones.models import Empleados, Puestos, Rangos, Usuarios, TiposEvaluaciones, Departamentos, Fechas,Rutas,Evaluaciones, Divisiones, Sucursales, Objetivos,CalificacionesGenerales,ComentariosAreas, CalificacionesAreas,ComentariosGenerales, NumerosEvaluaciones, Areas, Apartados, Seguimiento, Fases, ComentariosObjetivos, Comentarios, CalificacionesObjetivos, Resultados,Calendario, CalendarioFijo, EvaluacionesAreas
from .models_mysql import Empleado,EvaluacionesAntiguos,RutaEvalua,ObjetivosAntiguos,ApartadosMes, ApartadosAntiguos, Quejas, Evaluaobjetivos, Empleado
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q,F
from django.core import serializers

from django.core.exceptions import ObjectDoesNotExist

#Lo que sigue importe para el correo
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import smtplib
from django.utils.html import strip_tags
from django.db.models import Subquery


def index(request):
    return redirect(reverse('login'))



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
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    try:
        fecha = Fechas.objects.latest('id')
       # fecha = Fechas.objects.get(id=2026)
    except:
        fecha = []
    try :
        #Si encuentra la fecha de este mes echa ya no la hace
        fecha = Fechas.objects.get(mes=mes, anio=año)
    except:
        #Si no encuentra la fecha de este mes la crea y sus evaluaciones y comentarios
        #para hacerlo cada mes solo cambiar la variable dia por mes, esto solo es de practica
        if (fecha != []):
            if(mes != fecha.mes or año != fecha.anio):
                fechaAnterior = Fechas.objects.latest('id')
                #fechaAnterior = Fechas.objects.get(id=2026)
                fecha = Fechas(
                    mes = mes,
                    anio = año,
                    version = fecha.version + 1
                )
                fecha.save()
                evaluacionesAnteriores = EvaluacionesAreas.objects.filter(fecha_id=fechaAnterior.id)
                fechaNueva = Fechas.objects.latest('id')
                for evaluacion in evaluacionesAnteriores:
                    #aqui validar que estatus tiene el empleado y si es 0 no se agrega una evaluacion
                    empleado = Empleados.objects.get(no_emp=evaluacion.empleado_id)
                    if empleado.estatus == 1:
                        ev = EvaluacionesAreas (
                            fecha_id = fechaNueva.id,
                            empleado_id = evaluacion.empleado_id,
                            estatus = 1,
                            tipoEvaluacion_id = evaluacion.tipoEvaluacion_id,
                            ruta_id = evaluacion.ruta_id,
                            estado_id = 1
                        )
                        ev.save()
        else:
            fecha = Fechas(
                    mes = mes,
                    anio = año,
                    version = 1
                )
            fecha.save()

    # Obtener la cantidad de empleados por departamento y ordenarlos por departamento
    cantidad = Empleados.objects.filter(estatus=1).values('departamento_id').annotate(cantidad=Count('id')).order_by('departamento_id')
    departamentos_con_empleados = [c['departamento_id'] for c in cantidad]
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    ultimaFecha = Fechas.objects.get(mes=mes, anio=año)



    #DESDE AQUI PARA SABER QUE EMPLEADOS NO SE HAN CALIFICADO
    #obtener al usuario logueado
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp
    #empleado logueado
    empleado= Empleados.objects.get(no_emp=no_emp)    
    
    evaSegui = []
    evaluacionesNuevas=[]
            
    if (empleado.departamento_id == 11):
        try:
            evaluacionesNuevas= EvaluacionesAreas.objects.filter(Q(fecha_id=ultimaFecha.id) & Q(estatus=1))
        except:
            evaSegui = []
            evaluacionesNuevas=[]
    else:
        try:
            seguimientos = Rutas.objects.filter(evaluador_id=empleado.no_emp)
            evaSegui = []
            if seguimientos.exists():
                for segui in seguimientos:
                    evaluacionesNuevas = EvaluacionesAreas.objects.filter(Q(estatus=1) & Q(fecha_id=ultimaFecha.id) & Q(ruta_id=segui.id))
                    evaSegui.extend(evaluacionesNuevas)
                    evaluacionesNuevas = evaSegui
            else:
                evaluaciones=[]
        except:
            evaSegui = []
            evaluacionesNuevas=[]
    
    #HASTA AQUI PARA SABER QUE EMPLEADOS NO SE HAN CALIFICADO

    
    #ASIGNAR EL MISMO CALENDARIO A AMBOS
    try: 
        departamentos = Departamentos.objects.filter(id__in=departamentos_con_empleados)
        
        calendario = Calendario.objects.get(fecha_id=ultimaFecha.id, tipo=1)
    except:
        calendario=[]
        
    # TRAER DATOS INDIVIDUALES DE LOS ULTIMOS 3 RESULTADOS
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    fechaNecesaria = Fechas.objects.get(mes=mes, anio=año)
    fechas_anteriores = Fechas.objects.filter(id__lt=fechaNecesaria.id).order_by('-id')[:2]
    
    fechas = list(fechas_anteriores) + [fechaNecesaria]
    # fechas = Fechas.objects.filter()
    
    ids_fechas = [fecha.id for fecha in fechas]
    
    nvsFecha = Fechas.objects.filter(id__in=ids_fechas)


    try:
        # Filtrar las evaluaciones utilizando los IDs de las fechas
        evaluaciones1 = EvaluacionesAreas.objects.filter(fecha_id__in=ids_fechas, empleado_id = no_emp).select_related('fecha', 'empleado', 'tipoEvaluacion', 'ruta',)
        
        
        try:
            seguimiento0= Rutas.objects.get(id=evaluaciones1[0].ruta_id)
            resultados0 = CalificacionesGenerales.objects.filter(evaluacion_id=evaluaciones1[0].id).select_related('evaluacion')
            fecha1 = Fechas.objects.get(id=ids_fechas[0])
        except:
            seguimiento0 = []
            resultados0 = []
            fecha1 = []
        
        try:
            seguimiento1= Rutas.objects.get(id=evaluaciones1[1].ruta_id)
            resultados1 = CalificacionesGenerales.objects.filter(evaluacion_id=evaluaciones1[1].id).select_related('evaluacion')
            fecha2 = Fechas.objects.get(id=ids_fechas[1])
        except:
            seguimiento1 = []
            resultados1 = []
            fecha2 = []
        
        try:
            seguimiento2= Rutas.objects.get(id=evaluaciones1[2].ruta_id)
            resultados2 = CalificacionesGenerales.objects.filter(evaluacion_id=evaluaciones1[2].id).select_related('evaluacion')
            fecha3 = Fechas.objects.get(id=ids_fechas[2])
        except:
            seguimiento2 = []
            resultados2 = []
            fecha3 = []
        
    except:
        resultados0 = []
        resultados1 = []
        resultados2 = []
        evaluaciones1 = []
        seguimiento0 = []
        seguimiento1 = []
        seguimiento2 = []
        seguimientos = []
        fecha1 = []
        fecha2 = []
        fecha3 = []
    #FIN RESULTADOS INDIVIDUALES ########################3
    
    # PROMEDIAR RESULTADOS DE LAS EVALUACIONES DE 3 ULTIMOS MESES
    nvs_id_fechas = [fecha.id for fecha in nvsFecha]
    promedios = []
    evaluaciones2 = EvaluacionesAreas.objects.filter(fecha_id__in=nvs_id_fechas) 
    if (evaluaciones2): 
        suma = 0
        for fechas in nvs_id_fechas:
            evaluaciones2 = EvaluacionesAreas.objects.filter(fecha_id=fechas)
            ids_eva = [evaluaciones3.id for evaluaciones3 in evaluaciones2]
            resultados = CalificacionesGenerales.objects.filter(evaluacion_id__in=ids_eva)
            if (resultados):
                suma=0
                for resultado in resultados:
                    suma += resultado.calificacion_evaluador
                fecha = Fechas.objects.get(id=fechas)    
                if(suma > 0):
                    promedio = round((suma / len(resultados)), 2)
                    promedios.append((promedio, fecha.mes, fecha.anio))
    else:
        promedios = []        
    
    
    # PROMEDIAR RESULTADOS POR DEPARTAMENTOO
    promedios_departamento = []
    evaluaciones2 = EvaluacionesAreas.objects.filter(fecha_id__in=nvsFecha)
    if (evaluaciones2):
        departamentos = Departamentos.objects.filter(estatus=1)
        for departamento in departamentos:
            suma = 0
            for fechas in nvs_id_fechas:
                evaluaciones2 = EvaluacionesAreas.objects.filter(fecha_id=fechas, empleado__departamento_id=departamento.id)
                ids_eva = [evaluaciones3.id for evaluaciones3 in evaluaciones2]
                fecha = Fechas.objects.get(id=fechas) 
                resultados = CalificacionesGenerales.objects.filter(evaluacion_id__in=ids_eva)
                if (resultados):
                    suma=0
                    resul=0
                    for resultado in resultados:
                        if (resultado != -1):
                            suma += resultado.calificacion_evaluador
                            resul=resul+1
                    if(suma > 0):
                        promedio = round((suma / resul), 2)
                        promedios_departamento.append((promedio, fecha.mes, fecha.anio, departamento.nombre, departamento.id))
                    else:
                        promedios_departamento.append((0, fecha.mes, fecha.anio, departamento.nombre, departamento.id))
                else:
                    promedios_departamento.append((0, fecha.mes, fecha.anio, departamento.nombre, departamento.id))
    
    
    
    
    #AQUI PARA ENVIAR LOS RECORDATORIOS DE LAS EVALUACIONES
    calendarioFijo = []
    try:
        calendarioFijo = CalendarioFijo.objects.get(calendario_id=calendario.id)
        
        fecha_fija = calendarioFijo.jefesInicio

        # Desglosar la fecha fija
        dia_fijo = fecha_fija.day    
        mes_fijo = fecha_fija.month
        anio_fijo = fecha_fija.year
        if (calendarioFijo.status == 1 and dia == dia_fijo and mes == mes_fijo and año == anio_fijo):
            enviarCorreoTodos(calendario.id)
        else: 
            print("no envio correos")
    except:
        print("No se pudo enviar el correo, no hay calendarios")
        
    context ={
        'empleados': empleados,
        'departamentos': departamentos,
        'cantidad': cantidad,
        'empleado': empleado,
        'calendario': calendarioFijo,
        'evaluaciones1': evaluaciones1,
        'resultados0': resultados0,
        'resultados1': resultados1,
        'resultados2': resultados2,
        'seguimiento0': seguimiento0,
        'seguimiento1': seguimiento1,
        'seguimiento2': seguimiento2,
        'promedios': promedios,
        'promedios_departamento': promedios_departamento,
        'fechas': nvsFecha,
        'evaluacionesNuevas': evaluacionesNuevas,
    }
    return render(request, 'dashboard.html', context)

def enviarCorreoTodos(id):
    
    calendarioFijo = CalendarioFijo.objects.get(calendario_id=id)
    correos2 = []
    empleados= Empleados.objects.filter(estatus=1)
    correos2 =['zlara@cesehsa.com.mx','bsistemas@cesehsa.com'] 
        
    correos = list(empleados.values_list('correo', flat=True))
    correos3 =['zlara@cesehsa.com.mx','bsistemas@cesehsa.com'] 
    
    
    template = render_to_string('plantillaCorreoRecordatorio.html', {
        'calendarioFijo': calendarioFijo
    })

    try:
        email = EmailMultiAlternatives(
        subject='Sistema de desempeño',
        body=strip_tags(template),  # Cuerpo de texto plano para clientes de correo que no admiten HTML
        from_email=settings.EMAIL_HOST_USER,
        #TODOS LOS CORREOS HASTA EL MOMENTO SE ME ENVIAN A MI, HACER DESPUES QUE SE MANDEN AL CORREO DEL EVALUADOR SOLO PONER EL CORREO DE EVALUADOR
        #PONER VARIABLE correo
        to=['zlara@cesehsa.com.mx'],
        # bcc=correos2
        # to=['zlara@cesehsa.com.x'],
        # bcc=correos
        )
        # email.fail_silently = False
        email.attach_alternative(template, "text/html")
        email.send()
        calendarioFijo.status = 2
        calendarioFijo.save()
    except:
        print("No se pudo enviar el correo")
        
    

#Muestra la vista para crear empleados
#Manda los datos necesarios para que se pueda crear un empleado
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def altaEmpleados(request):
    puestos = Puestos.objects.all().order_by('nombre')
    rangos = Rangos.objects.all().order_by('nombre')
    departamentos = Departamentos.objects.all().order_by('nombre')
    empleados = Empleados.objects.latest('no_emp')
    no_empleado= empleados.no_emp + 1
    divisiones = Divisiones.objects.all().order_by('nombre')
    sucursales = Sucursales.objects.all().order_by('nombre')
    return render(request, 'altaEmpleados.html', {'formulario': crearEmpleado(), 'puestos': puestos, 'rangos': rangos, 'departamentos': departamentos, 'no_empleado': no_empleado, 'divisiones': divisiones, 'sucursales': sucursales})


#Muestra la vista donde esta esta la tabla con todos los empleados
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def listaEmpleados(request):
    empleados = Empleados.objects.filter(estatus=1).order_by('no_emp')
    return render(request, 'listaEmpleados.html', {'empleados': empleados})


# Función para iniciar sesión
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': EmailAuthenticationForm()})
    else:
        return render(request, 'login.html',{'form', EmailAuthenticationForm()})

# Función para cerrar sesión
@login_required  
def salir(request):
    logout(request)
    return redirect('/')

#no la ocupo creo
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def verEmpleados(request):
    empleados = Empleados.objects.filter(estatus=1)
    return render(request, 'listaEmpleados.html', {'empleados': empleados})


#Muestra principal de las evaluaciones, manda a la vista de evaluaciones.html
#Es donde se muestran de manera general las evaluaciones que se han asignado a los empleados
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or u.no_emp == 101 or  u.departamento_id == 39, login_url='/informacion/')
def evaluaciones(request):
    empleados = Empleados.objects.filter(estatus=1)
    empleados = Empleados.objects.filter(estatus=1)
    fases = Fases.objects.all()
    
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    # fechas = Fechas.objects.get(mes=mes, anio=año)
    # evaluaciones = Evaluaciones.objects.filter(fecha_id=fechas.id).select_related('fecha', 'empleado', 'numeroEvaluacion', 'seguimiento', 'fase')
    fechas = Fechas.objects.order_by('-id')[:3]
    # fechas = Fechas.objects.filter()
    ids_fechas = [fecha.id for fecha in fechas]
    hayResultados = False

    try: 
        
        # Filtrar las evaluaciones utilizando los IDs de las fechas
        evaluaciones = EvaluacionesAreas.objects.filter(fecha_id__in=ids_fechas).order_by('fecha_id','empleado_id').select_related('fecha', 'empleado', 'tipoEvaluacion', 'ruta', 'estado')
        # for eva in evaluaciones:
        #     print(eva.id)
        seguimientos = Rutas.objects.all()
        resultados = []
        try:
            resultados= CalificacionesGenerales.objects.all()
            hayResultados = True
        except:
            resultados = []
        
        evaluaciones = EvaluacionesAreas.objects.filter(id__in=[eva.id for eva in evaluaciones]).annotate(empleado_nombre=F('empleado__nombre')).order_by('fecha_id','empleado_nombre')
    except:
        evaluaciones = []
        seguimientos = []
        fecha1 = []
        fecha2 = []
        fecha3 = []
    try:
        fecha1 = Fechas.objects.get(id=ids_fechas[0])
    except:
        fecha1 = []
    try:
        fecha2 = Fechas.objects.get(id=ids_fechas[1])
    except:
        fecha2 = []
    try:
        fecha3 = Fechas.objects.get(id=ids_fechas[2])   
    except:
        fecha3 = []
    
    
    return render(request, 'evaluaciones.html', {'empleados': empleados, 'fases': fases, 'evaluaciones': evaluaciones, 'seguimientos': seguimientos, 'fechas': fechas, 'fecha1': fecha1, 'fecha2': fecha2, 'fecha3': fecha3, 'resultados': resultados})

  
#Creo que no lo ocupo y ocupo el de abajo
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
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
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
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
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def asignarEvaluacion(request):
    fecha = Fechas.objects.latest('id')
    empleados = Empleados.objects.filter(estatus=1).order_by('nombre')
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
    siHayBono = False
    siHayResultados = False
    
    for o in obj:
        if o.apartado_id == 4:
            siHayBono = True
        if o.apartado_id == 5:
            siHayResultados = True
    fechas = Fechas.objects.all()
            
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
        'sumCL': sumCL,
        'siHayBono': siHayBono,
        'siHayResultados': siHayResultados,
        'fechas': fechas
    }
    return render(request, 'asignarEvaluacion.html',context)


# Lo ocupo en asignarEvaluacion.html y editarEvaluacion.html para que se muestren los objetivos de acuerdo al id de la evaluacion seleccionada
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def obtener_datos_evaluacion(request):
    if request.method == 'GET':
        evaluacion_id = request.GET.get('evaluacion_id')
        # Convierte el ID de la evaluación a entero
        evaluacion_id = int(evaluacion_id)
        
        evaluaciones= NumerosEvaluaciones.objects.get(id=evaluacion_id)
        
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
            'sumaCL': sumaCL,
            'estatus': evaluaciones.estatus
        }
        return JsonResponse(data)


#Este creo que ya no lo ocupo
#Es para guardar los objetivos separados en apartados en la base de datos
#Creo que ya no se ocupa por que me dio error en el servidor y lo cambie por el que esta abajo
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/') 
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
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def guardarEvaluacionBD(request):
    if request.method == 'POST':
        try:
            # Obtener los datos de los arreglos desde el formulario
            arregloBonos_str = request.POST.get('arregloBonos')
            arregloCLs_str = request.POST.get('arregloCLs')
            arregloKPIs_str = request.POST.get('arregloKPIs')
            arregloOKRs_str = request.POST.get('arregloOKRs')
            arregloResultados_str = request.POST.get('arregloResultados')
            intendencia = request.POST.get('intendencia')
            bandera=1
            
            #bandera 1 significa que no es de intendencia
            #bandera 2 significa que es de intendencia
            
            if intendencia == "0" :
                bandera=2
            # Convertir las cadenas JSON a diccionarios
            arregloBonos = json.loads(arregloBonos_str)
            arregloCLs = json.loads(arregloCLs_str)
            arregloKPIs = json.loads(arregloKPIs_str)
            arregloOKRs = json.loads(arregloOKRs_str)
            arregloResultados = json.loads(arregloResultados_str)
            
            if bandera==2:
                evaluacion = NumerosEvaluaciones(
                estatus=2,
                fechaCreacion=datetime.now()
                )
                evaluacion.save()
            else:
                evaluacion = NumerosEvaluaciones(
                estatus=1,
                fechaCreacion=datetime.now()
                )
                evaluacion.save()
            

            numeroEvaluacion = NumerosEvaluaciones.objects.latest('id')
            
            estatuS=1
                
            # Ahora puedes iterar sobre los arreglos y acceder a los datos
            for item in arregloOKRs:
                objetivo = Objetivos(
                    objetivo=item['objetivo'],
                    metrica=item['metrica'],
                    valor=item['valor'],
                    estatus=estatuS,
                    apartado_id=1,
                    numeroEvaluacion_id=numeroEvaluacion.id
                )
                objetivo.save()

            for item in arregloKPIs:
                objetivo = Objetivos(
                    objetivo=item['objetivo'],
                    metrica=item['metrica'],
                    valor=item['valor'],
                    estatus=estatuS,
                    apartado_id=2,
                    numeroEvaluacion_id=numeroEvaluacion.id
                )
                objetivo.save()
                
            if bandera==1:
                for item in arregloCLs:
                    objetivo = Objetivos(
                        objetivo=item['objetivo'],
                        metrica=item['metrica'],
                        valor=item['valor'],
                        estatus=estatuS,
                        apartado_id=3,
                        numeroEvaluacion_id=numeroEvaluacion.id
                    )
                    objetivo.save()

            for item in arregloBonos:
                objetivo = Objetivos(
                    objetivo=item['objetivo'],
                    metrica=item['metrica'],
                    valor=item['valor'],
                    estatus=estatuS,
                    apartado_id=4,
                    numeroEvaluacion_id=numeroEvaluacion.id
                )
                objetivo.save()

            for item in arregloResultados:
                objetivo = Objetivos(
                     objetivo=item['objetivo'],
                    metrica=item['metrica'],
                    valor=item['valor'],
                    estatus=estatuS,
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
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def editarEmpleado(request, id):
    empleado = Empleados.objects.get(no_emp=id)
    puestos = Puestos.objects.filter(estatus=1).order_by('nombre')
    rangos = Rangos.objects.all().order_by('nombre')
    departamentos= Departamentos.objects.filter(estatus=1).order_by('nombre')
    divisiones = Divisiones.objects.all().order_by('nombre')
    sucursales = Sucursales.objects.all().order_by('nombre')
    return render(request, 'editarEmpleado.html', {'empleado': empleado, 'puestos': puestos, 'rangos': rangos, 'departamentos': departamentos, 'divisiones': divisiones, 'sucursales': sucursales})


#Edita un empleado de la base de datos en las tablas de empleados y usuarios(usuarios de django)
# De acuerdo con los cambios de la vista de editarEmpleado.html
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
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
    division_id = int(request.POST['division'])
    sucursal_id = int(request.POST['sucursal'])

    empleado = Empleados.objects.get(no_emp=no_emp)
    empleado.nombre = nombre
    empleado.apellido_paterno = apellido_paterno
    empleado.apellido_materno = apellido_materno
    empleado.password = password
    empleado.estatus = estatus
    empleado.puesto_id = puesto_id
    empleado.rango_id = rango_id
    empleado.departamento_id = departamento_id
    empleado.division_id = division_id
    empleado.sucursal_id = sucursal_id


    usuario = Usuarios.objects.get(no_emp=no_emp)
    usuario.last_name = apellido_paterno
    usuario.username =  no_emp
    usuario.first_name = nombre
    usuario.email = correo
    usuario.rango_id = rango_id
    usuario.departamento_id = departamento_id
    usuario.password = make_password(password)

    
    empleado.save()
    usuario.save()
    empleados = Empleados.objects.filter(estatus=1)
    return redirect(reverse('listaEmpleados'))

#Elimina un empleado de la base de datos de manera lógica ya que solo cambia su estatus a 0
#Se recibe el id del empleado que se quiere eliminar  
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
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
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
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
    division_id = int(request.POST['division'])
    sucursal_id = int(request.POST['sucursal'])

    usuario = Usuarios.objects.create_user(username=no_emp, email=correo, password=password, first_name=nombre, last_name=apellido_paterno, no_emp=no_emp, rango_id=rango_id, departamento_id=departamento_id)

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
        estatus=estatus,
        division_id=division_id,
        sucursal_id=sucursal_id
    )
    empleado.save()
    usuario.save()
    return redirect(reverse('listaEmpleados'))

#Muestra la vista para crear las rutas de evaluacion y aquellas rutas de evaluacion existentes
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def rutaEvaluacion(request):
    empleados = Empleados.objects.filter(estatus=1)
    rutas = Rutas.objects.all()
    return render(request, 'rutaEvaluacion.html', {'empleados': empleados, 'rutas': rutas})


#Guarda la ruta de evaluacion que se a escogido en la vista de rutaEvaluacion.html y redirige a la vista de evaluaciones
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def guardarRutaEvaluacion(request):
    evaluador1 = int(request.POST['evaluador1'])

    ruta = Rutas(
        evaluador_id=evaluador1,
        estatus = 1
    )
    ruta.save()

    return redirect(reverse('evaluaciones'))

#Lo ocupo para vista de asignarEvaluacion.html que se puedan ver los evaluadores de cada seguimiento de acuerdo al id seleccionado
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def obtener_datos_seguimiento(request):
    if request.method == 'GET':
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
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def obtener_datos_evaluaciones(request):
    if request.method == 'GET':
        empleado_id = request.GET.get('empleado_id')
        fecha_id = int(request.GET.get('fecha_id'))
        numeroEvaluacion = request.GET.get('numeroEvaluacion_id')
        
        empleado = Empleados.objects.get(no_emp=empleado_id)    
        evaluaciones = Evaluaciones.objects.filter(empleado_id=empleado_id)
        objetivos = Objetivos.objects.filter(numeroEvaluacion_id=numeroEvaluacion)
        eva = NumerosEvaluaciones.objects.get(id=numeroEvaluacion)
        estatus = eva.estatus
        
        bandera = 0
        if evaluaciones.exists():
            for evaluacion in evaluaciones:
                #print("las fechas son", evaluacion.fecha_id, fecha_id, evaluacion.fecha_id == fecha_id),
                if evaluacion.fecha_id == fecha_id:
                    bandera = 1
                    break

        for objetivo in objetivos:
            if objetivo.apartado_id == 4 and empleado.departamento_id not in [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]:
                bandera = 2
                if (empleado.rango_id != 4):
                    bandera = 3
                    
        if estatus == 2:
            if empleado.departamento_id != 13:
                bandera = 0
        else:
            if empleado.departamento_id == 13:
                bandera = 0
                
        data = {
            'bandera': bandera
        }
        return JsonResponse(data)
    



#Cuando se asigna una evaluacion a un empleado aqui se guarda la información, es para llenar la tabla de evaluaciones
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def guardarEvaluacionMensual (request):
    empleado_id = int(request.POST['empleado'])
    numeroEvaluacion_id = int(request.POST['numeroEvaluacion'])
    seguimiento_id = int(request.POST['seguimiento'])
    fecha = Fechas.objects.latest('id')
    fechass = int(request.POST['fechas'])
    fecha = Fechas.objects.get(id=fechass)
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
@login_required
#@user_passes_test(lambda u: u.departamento_id == 11, login_url='/informacion/')
def guardarEvaluacionEditada (request):
    #empleado_id = int(request.POST['empleado'])
    evaluacion = int(request.POST['eva'])
    # numeroEvaluacion_id = int(request.POST['numeroEvaluacion'])
    # ruta_id = int(request.POST['seguimiento'])
    # #fecha = Fechas.objects.latest('id')

    evaluacion = EvaluacionesAreas.objects.get(id=evaluacion)
    # evaluacion.ruta_id= ruta_id
    # evaluacion.tipoEvaluacion_id = numeroEvaluacion_id 
    # evaluacion.save()
    return redirect('reporteEvaluacion', args=[evaluacion.id])

@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def obtener_datos_evaluaciones_editada(request):
    if request.method == 'GET':
        empleado_id = request.GET.get('empleado_id')
        fecha_id = int(request.GET.get('fecha_id'))
        numeroEvaluacion = request.GET.get('numeroEvaluacion_id')
        ruta= request.GET.get('seguimiento_id')
        intendencia = request.GET.get('intendencia')
        fechaReal = int(request.GET.get('fechaReal'))
        eva_id = int(request.GET.get('eva_id'))
    
        empleado = Empleados.objects.get(no_emp=empleado_id)    
        evaluaciones = Evaluaciones.objects.filter(empleado_id=empleado_id)
        objetivos = Objetivos.objects.filter(numeroEvaluacion_id=numeroEvaluacion)
        
        try:
            # evaluacion = int(request.POST['eva'])
            # numeroEvaluacion_id = int(request.POST['numeroEvaluacion'])
            # ruta_id = int(request.POST['seguimiento_id'])
            # #fecha = Fechas.objects.latest('id')

            evaluacion = EvaluacionesAreas.objects.get(id=eva_id)
            evaluacion.ruta_id= ruta
            evaluacion.tipoEvaluacion_id = numeroEvaluacion 
            evaluacion.save()
            bandera = 0
        
        except:
            bandera = 1
            
        data = {
            'bandera': bandera
        }
        return JsonResponse(data)


#muestra la vista para crear una evaluacion en base a una existente
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def editarEvaluacion(request):
    try:
        numeroEvaluacion=NumerosEvaluaciones.objects.all()
        eva = NumerosEvaluaciones.objects.latest('id')
        obj = Objetivos.objects.filter(numeroEvaluacion_id = eva.id)
        valores = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
        sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
        sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()
    except:
        numeroEvaluacion = []
        obj = []
        valores = []
        sumOKR = 0
        sumKPI = 0
        sumCL = 0
        eva = []

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
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    fechh = Fechas.objects.get(mes=mes, anio=año)

    evaluacion = Evaluaciones.objects.filter(empleado_id=empleado.no_emp, fecha_id=fechh.id)
    objetivos = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id)
    seguimiento = Seguimiento.objects.filter(id=evaluacion.seguimiento_id)
    context ={ 
        "evaluacion": evaluacion,
        "objetivos": objetivos,
        "seguimiento": seguimiento
    }
    return render(request, 'evaluacionUsuario.html', {'evaluaciones': evaluaciones})




#Muestra la vista para editar la evaluación asignada, le manda toda la info de la evaluacion para que se pueda ver en lo que escoge el combo
@login_required
@user_passes_test(lambda u: u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def editarEvaluacionAsignada(request,id):
    idd = id
    empleados = Empleados.objects.filter(estatus=1)
    numeroEvaluacion = TiposEvaluaciones.objects.all()
    objetivos=Areas.objects.all()
    apartados = Apartados.objects.all()
    seguimientos = Rutas.objects.all()
    
    eva = EvaluacionesAreas.objects.get(id=idd)
    fechh = Fechas.objects.get(id=eva.fecha_id)
    numEva= TiposEvaluaciones.objects.get(id=eva.tipoEvaluacion_id)
    obj = Areas.objects.filter(tipoEvaluacion_id=eva.tipoEvaluacion_id)
    emp = Empleados.objects.get(no_emp= eva.empleado_id)
    rut = Rutas.objects.get(id=eva.ruta_id)
    
    sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
    sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
    sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()
    fechas = Fechas.objects.all()
    
    if (sumCL == None):
        sumCL = 0
        siHayCL = False
    else:
        siHayCL = True
        
    siHayBono = False
    siHayResultados = False
    
    for o in obj:
        if o.apartado_id == 4:
            siHayBono = True
        if o.apartado_id == 5:
            siHayResultados = True

    context = {
        'fechh': fechh,
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
        'siHayBono': siHayBono,
        'siHayResultados': siHayResultados,
        'fechas': fechas,
    }
    return render(request, 'editarEvaluacionAsignada.html', context)


#Muestra la vista de comentarios iniciales, donde pueden comentar los evaluadores 1 y los de capital humano a todos
@login_required
@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.departamento_id == 11 or  u.departamento_id == 39 , login_url='/informacion/')
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
    
    error=0
    permisos= False
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    fechh = Fechas.objects.get(mes=mes, anio=año)
    permisosVentas=0
    permisosTodos = 0
        
    try:
        calendario = Calendario.objects.get(fecha_id=fechh.id,tipo=2)
        if (calendario.comentariosInicialesInicio <= datetime.now().date() and calendario.comentariosInicialesFin >= datetime.now().date()):
            permisosVentas= 1
    except:
        error=4
        
    
    #calendario de todos esta vigente y que apartado si el de jefes o gerentes o ambos
    try:
        calendario = Calendario.objects.get(fecha_id=fechh.id,tipo=1)
        if (calendario.comentariosInicialesInicio <= datetime.now().date() and calendario.comentariosInicialesFin >= datetime.now().date()):
            permisosTodos = 1
    except:
        error=4   
        
    evaSegui = []
    error=0
    
    if (empleado.departamento_id in (14,15,16,17,18,19,20,21,22,23,24)):
        if (permisosVentas==1):
            try:
                if(empleado.no_emp == 275):
                  empleadosVentas= Empleados.objects.filter(departamento_id__in=(14,15,16,17,18,19,20,21,22,23,24), estatus=1)
                  evaSegui = Evaluaciones.objects.filter(estatus__in=(0,1), fecha_id=fechh.id, empleado_id__in=(empleadosVentas.values_list('no_emp', flat=True)))
                  #evaSegui.extend(evaluaciones)
                else: 
                    seguimientos = Seguimiento.objects.filter(Q(evaluador1_id=empleado.no_emp) |
                    Q(evaluador2_id=empleado.no_emp) |
                    Q(evaluador3_id=empleado.no_emp) |
                    Q(evaluador4_id=empleado.no_emp))
                    evaSegui = []
                    for segui in seguimientos:
                        evaluaciones = Evaluaciones.objects.filter(seguimiento_id=segui.id, estatus=0, fecha_id=fechh.id)
                        evaSegui.extend(evaluaciones)
            except:
                error=3
    else:
        if (empleado.departamento_id == 11 or empleado.no_emp == 283 ):
            if (permisosVentas==1):
                empleadosVentas = Empleados.objects.filter(departamento_id__in=(14,15,16,17,18,19,20,21,22,23,24), estatus=1)
                evaSegui.extend(Evaluaciones.objects.filter(estatus__in=(0,1), fecha_id=fechh.id, empleado_id__in=(empleadosVentas.values_list('no_emp', flat=True))))

            if (permisosTodos==1):
                empleadosGeneral = Empleados.objects.filter(departamento_id__in=(1,2,3,4,5,6,7,8,9,10,11,12,13,25), estatus=1)
                evaSegui.extend(Evaluaciones.objects.filter(estatus__in=(0,1), fecha_id=fechh.id, empleado_id__in=(empleadosGeneral.values_list('no_emp', flat=True))))
        else:
            if (permisosTodos==1):
                try:
                    seguimientos = Seguimiento.objects.filter(Q(evaluador1_id=empleado.no_emp) |
                    Q(evaluador2_id=empleado.no_emp) |
                    Q(evaluador3_id=empleado.no_emp) |
                    Q(evaluador4_id=empleado.no_emp))
                    evaSegui = []
                    for segui in seguimientos:
                        evaluaciones = Evaluaciones.objects.filter(seguimiento_id=segui.id, estatus=0, fecha_id=fechh.id)
                        evaSegui.extend(evaluaciones)
                except:
                    error=3
        
    evaSegui = Evaluaciones.objects.filter(id__in=[eva.id for eva in evaSegui]).annotate(empleado_nombre=F('empleado__nombre')).order_by('empleado_nombre')
    
        
    context ={
        "evaSegui": evaSegui,
        "empleado": empleado,
        "error": error,
    }

    return render(request, 'comentariosInicio.html', context)


#Guarda los comentarios iniciales de acuerdo a lo que se escriba en comentariosInicio.html
#se podría ocupar para guardar los comentarios de todos
@login_required
@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def guardar_comentarios_iniciales(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('comentarios'))
        comentariosGenerales = json.loads(request.POST.get('comentariosGenerales'))
        resultadoCL = json.loads(request.POST.get('resultadoCL'))

        numEva = request.POST.get('numeroEvaluacion')
        #Traer la evaluacion de mi base de datos
        evaluacion = Evaluaciones.objects.get(id=numEva)

        #obtener al empleado logueado
        usuario=1
        if request.user.is_authenticated:
            usuario= request.user.id
        usuario= Usuarios.objects.get(id=usuario)   
        empleado = Empleados.objects.get(no_emp=usuario.no_emp)
        #guardar en una variable el numero de empleado
        no_emp = empleado.no_emp
        
        # for res in resultadoCL:
        #     if (resultadoCL[id]!=0):
        
        if len(resultadoCL) != 0:
            #AQUI SE GUARDAN LAS RESPUESTAS DE CAPITAL HUMANO PARA CULTURA LABORAL
            for item in resultadoCL:
                if item['id'] != '0':  # Asegúrate de que 'id' es una cadena
                    try:
                        calificacionesObj= CalificacionesObjetivos.objects.get(objetivo_id=item['id'], evaluacion_id=evaluacion.id)
                        calificacionesObj.calificacion = item['value']
                        quienCalifica = no_emp
                        calificacionesObj.save()
                    except:
                        respuesta = CalificacionesObjetivos(
                            calificacion=item['value'],
                            fechaCalificacion=datetime.now(),
                            estatus=9,
                            fecha_id=evaluacion.fecha_id,
                            objetivo_id=item['id'],
                            quienCalifica_id=no_emp,
                            evaluacion_id=evaluacion.id
                        )
                        respuesta.save()
                else:
                    print("no pasa la parte de guardar calificacion de CL")          
            
            
        #guardar los comentarios por cada objetivo
        for item in data:
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
        
        #Cambiar el estatus de mi evaluacion aqui deberia de cambiar en autoevaluacion a otro estatus y fase para saber en que proceso se encuentra
        if empleado.departamento_id != 11 and empleado.no_emp != 283 and empleado.no_emp != 275:
            evaluacion.estatus = 1
            evaluacion.fase_id = 2
            evaluacion.save()

        if (empleado.no_emp == 275 or empleado.no_emp == 283 or empleado.departamento_id == 11):
            evaluacion.fase_id = 2
            evaluacion.save()
            
        #Aqui guardo los comentarios generales y tendria que hacer algo muy parecido para comentarios de logros
        if len(comentariosGenerales) != 0:
            comentarios = Comentarios.objects.get(evaluacion_id=evaluacion.id)
            if empleado.departamento_id == 11:
                nuevo_comentario = comentarios.comentario_capitalHumano + " -> " + comentariosGenerales[0]['comentario']
                comentarios.comentario_capitalHumano = nuevo_comentario.strip()  # Elimina posibles espacios en blanco al inicio y al final
            else:
                if empleado.no_emp == 283:
                    nuevo_comentario = comentarios.comentario_calidad + " -> " + comentariosGenerales[0]['comentario']
                    comentarios.comentario_calidad = nuevo_comentario.strip()
                else:
                    comentarios.comentario_evaluador1 = comentariosGenerales[0]['comentario']
            comentarios.save()



        return JsonResponse({'message': 'Comentarios guardados exitosamente'})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)


#Mostrar la vista de la autoevaluación y sus comentarios
@login_required
def autoevaluacion (request):
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleado= Empleados.objects.get(no_emp=no_emp)

    siHayBono = False
    siHayResultados = False
    idCL = 0
    objCL=""
    metCL=""
    valCL=""
    comentCL= []
    #Checar que este dentro de la fecha que indique capital humano, si no que no pueda entrar, y el error sea 4 y muestre
    #un mensaje que diga que no puede entrar a la autoevaluacion por que no esta en la fecha indicada
    error=0
    permisos= False
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    fechh = Fechas.objects.get(mes=mes, anio=año)
    tipo=0
    

    if (empleado.departamento_id in (14,15,16,17,18,19,20,21,22,23,24)):
        try:
            calendario = Calendario.objects.get(fecha_id=fechh.id,tipo=2)
            if (calendario.empleadosInicio <= datetime.now().date() and calendario.empleadosFin >= datetime.now().date()):
                permisos= True
            else:
                error=4
        except:
            error=5
    else:
        try: 
            calendario = Calendario.objects.get(fecha_id=fechh.id,tipo=1)
            if (calendario.empleadosInicio <= datetime.now().date() and calendario.empleadosFin >= datetime.now().date()):
                permisos= True
            else:
                error=4
        except:
            error=5
    #        tipo= evaluacion.numeroEvaluacion.estatus
    # #Es para saber si la autoevaluacion ya fue contestada o no
    # seguimiento= Seguimiento.objects.get(id=evaluacion.seguimiento_id)
    # comentariosGenerales = Comentarios.objects.get(evaluacion_id=evaluacion.id)
    # resultados = Resultados.objects.get(evaluacion_id=evaluacion.id)
    # obj = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id)
    # obj = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id).prefetch_related('comentariosobjetivos_set', 'calificacionesobjetivos_set')
    
    if permisos:    
        try: 
            # AQUI TENGO QUE VALIDAR QUE LA EVALUACION ESTE EN LA FASE 2 PARA QUE DESPUES DE CONTESTADA YA NO SE PUEDA CONTESTAR
            # evaluacion= Evaluaciones.objects.filter(empleado_id=empleado.no_emp, fecha_id=fecha.id, estatus__in=[0, 1, 2], fase_id__in=[1,2])
            evaluacion= Evaluaciones.objects.get(empleado_id=empleado.no_emp, fecha_id=fechh.id)
            tipo= evaluacion.numeroEvaluacion.estatus
            
            #Es para saber si la autoevaluacion ya fue contestada o no
            if (evaluacion.fase_id < 3 ):
                if (evaluacion.estatus < 3):
                    seguimiento= Seguimiento.objects.get(id=evaluacion.seguimiento_id)
                    comentariosGenerales = Comentarios.objects.get(evaluacion_id=evaluacion.id)
                    obj = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id)
                    obj= Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id).prefetch_related('comentariosobjetivos_set','calificacionesobjetivos_set')

                    sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
                    sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
                    sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()

                    for o in obj:
                        if o.apartado_id == 3:
                            objCL += o.objetivo
                            metCL += o.metrica
                            valCL = o.valor
                            idCL = o.id

                    for o in obj:
                        if o.apartado_id == 4:
                            siHayBono = True
                        if o.apartado_id == 5:
                            siHayResultados = True

                    error = 0
                else:
                    evaluacion = []
                    obj = []
                    comentariosGenerales = []
                    sumOKR = []
                    sumKPI = []
                    sumCL = []
                    seguimiento = []
                    error=6

            else:
                error=1
                evaluacion = []
                obj = []
                comentariosGenerales = []
                sumOKR = []
                sumKPI = []
                sumCL = []
                seguimiento = []
                error=6
            
        except:
            error=2
            evaluacion = []
            obj = []
            comentariosGenerales = []
            sumOKR = []
            sumKPI = []
            sumCL = []
            seguimiento = []
    else:
        error=4
        evaluacion = []
        obj = []
        comentariosGenerales = []
        sumOKR = []
        sumKPI = []
        sumCL = []
        seguimiento = []


    context ={
        "evaluacion": evaluacion,
        "obj": obj,
        "empleado": empleado,
        "sumOKR": sumOKR,
        "sumKPI": sumKPI,
        "sumCL": sumCL,
        "siHayBono": siHayBono,
        "siHayResultados": siHayResultados,
        "comentariosGenerales": comentariosGenerales,
        "seguimiento": seguimiento,
        "objCL": objCL,
        "metCL": metCL,
        "valCL": valCL,
        "idCL": idCL,
        "error": error,
        "tipo": tipo
    }
    return render(request, 'autoevaluacion.html', context)

def guardarAutoevaluacion(request):
    if request.method == 'POST':
        comentarios = json.loads(request.POST.get('comentarios'))
        comentariosGenerales = json.loads(request.POST.get('comentariosGenerales'))
        logros = json.loads(request.POST.get('logros'))
        respuestas = json.loads(request.POST.get('respuestas'))
        numEva = request.POST.get('numeroEvaluacion')
        total = request.POST.get('total')

        #Traer la evaluacion de mi base de datos
        evaluacion = Evaluaciones.objects.get(id=numEva)

        #obtener al empleado logueado
        usuario=1
        if request.user.is_authenticated:
            usuario= request.user.id
        usuario= Usuarios.objects.get(id=usuario)   
        empleado = Empleados.objects.get(no_emp=usuario.no_emp)
        #guardar en una variable el numero de empleado
        no_emp = empleado.no_emp

        #guardar los comentarios por cada objetivo
        for item in comentarios:
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

        #Cambiar el estatus y la fase de la autoevaluacion
        evaluacion.estatus = 3
        evaluacion.fase_id = 3
        evaluacion.save()

        #Aqui guardo los comentarios generales y tendria que hacer algo muy parecido para comentarios de logros
        if len(comentariosGenerales) != 0:
            comentarios = Comentarios.objects.get(evaluacion_id=evaluacion.id)
            comentarios.comentario_autoevaluado = comentariosGenerales[0]['comentario']
            comentarios.save()

        if len(logros) != 0:
            comentarios = Comentarios.objects.get(evaluacion_id=evaluacion.id)
            comentarios.logros = logros[0]['logro']
            comentarios.save()

        #Aqui guardo las respuestas de la autoevaluacion
        for item in respuestas:
            respuesta = CalificacionesObjetivos(
                calificacion = item['respuesta'],
                fechaCalificacion = datetime.now(),
                estatus = 1,
                fecha_id = evaluacion.fecha_id,
                objetivo_id= item['id'],
                quienCalifica_id = no_emp,
                evaluacion_id = evaluacion.id
            )
            respuesta.save()

        #También guardar la calificacion total de la autoevaluacion
        try: 
            calificaciones = Resultados.objects.get(evaluacion_id=evaluacion.id)
            calificaciones.calificacion_autoevaluado = total
            calificaciones.estatus = 1
            calificaciones.save()
        except:
            calificaciones = Resultados (
                calificacion_autoevaluado = total,
                calificacion_evaluador1 = -1,
                calificacion_evaluador2 = -1,
                calificacion_evaluador3 = -1,
                calificacion_evaluador4 = -1,
                calificacion_director = -1,
                estatus = 1,
                evaluacion_id = evaluacion.id
            )
            calificaciones .save()
        # HASTA AQUIIII TOSOS SIRVEEE LO DE ARRIBA, NO BORRAR Y DESCOMENTARIZAR CUANDO ACABE


        return JsonResponse({'message': 'Comentarios guardados exitosamente'})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def enviarCorreo(request):
    if request.method == 'POST':
        numEva = request.POST.get('numeroEvaluacion')
        evaluacion = Evaluaciones.objects.get(id=numEva)
        seguimiento = Seguimiento.objects.get(id=evaluacion.seguimiento_id)
        evaluador1 = Empleados.objects.get(no_emp=seguimiento.evaluador1_id)
        nombre = evaluador1.nombre
        correo= evaluador1.correo
        empleado = Empleados.objects.get(no_emp=evaluacion.empleado_id)
        correoEmp = empleado.correo 
        
        if empleado.departamento_id in (14,15,16,17,18,19,20,21,22,23,24):
            cal = Calendario.objects.get(fecha_id=evaluacion.fecha_id, tipo=2)
        else:
            cal = Calendario.objects.get(fecha_id=evaluacion.fecha_id, tipo=1)
                
        template = render_to_string('plantillaCorreo.html', {
            'nombre': nombre,
            'empleado': empleado,
            'correo': correo,
            'evaluador': evaluador1,
            'calendario': cal,
        })

        email = EmailMultiAlternatives(
        subject='Sistema de desempeño',
        body=strip_tags(template),  # Cuerpo de texto plano para clientes de correo que no admiten HTML
        from_email=settings.EMAIL_HOST_USER,
        #TODOS LOS CORREOS HASTA EL MOMENTO SE ME ENVIAN A MI, HACER DESPUES QUE SE MANDEN AL CORREO DEL EVALUADOR SOLO PONER EL CORREO DE EVALUADOR
        #PONER VARIABLE correo
        to=['bsistemas@cesehsa.com'],
        cc=['zlara@cesehsa.com.mx']
        # to=[correo],
        # cc=[correoEmp]
        )
        # email.fail_silently = False
        email.attach_alternative(template, "text/html")
        email.send()
    
        return JsonResponse({'message': 'Comentarios guardados exitosamente'})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def enviarCorreoFin(request):
    if request.method == 'POST':
        numEva = request.POST.get('numeroEvaluacion')        
        evaluacion = EvaluacionesAreas.objects.get(id=numEva)
        ruta = Rutas.objects.get(id=evaluacion.ruta_id)
        evaluador1 = Empleados.objects.get(no_emp=ruta.evaluador_id)
        empleado = Empleados.objects.get(no_emp=evaluacion.empleado_id)
        correoEmp = empleado.correo 
        resultados = CalificacionesGenerales.objects.get(evaluacion_id=evaluacion.id)
        try: 
            comentarios = ComentariosGenerales.objects.get(evaluacion_id=evaluacion.id)
        except: 
            comentarios = "Sin comentarios"
                
        template = render_to_string('plantillaCorreoFin.html', {
            'empleado': empleado,
            'evaluador1': evaluador1,
            'resultados': resultados,
            'comentarios': comentarios,
        })

        email = EmailMultiAlternatives(
        subject='Sistema de desempeño',
        body=strip_tags(template),  # Cuerpo de texto plano para clientes de correo que no admiten HTML
        from_email=settings.EMAIL_HOST_USER,
        #TODOS LOS CORREOS HASTA EL MOMENTO SE ME ENVIAN A MI, HACER DESPUES QUE SE MANDEN AL CORREO DEL EVALUADOR SOLO PONER EL CORREO DE EVALUADOR
        #PONER VARIABLE correo
        #to=['zlara@cesehsa.com.mx'],
        to=[correoEmp],
        )
        # email.fail_silently = False
        email.attach_alternative(template, "text/html")
        email.send()
    
        return JsonResponse({'message': 'Comentarios guardados exitosamente'})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def traerDatosEmpleado(request):
    if request.method == 'GET':
        no_emp = request.GET.get('no_emp')
        try:
            empleado = Empleados.objects.get(no_emp=no_emp)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'El empleado no existe'}, status=404)

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
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)    

@login_required
@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def obtener_datos_evaluacion_comentarios(request):
    if request.method == 'GET':
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
        
        cal_OKR = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=1).select_related('objetivo','quienComenta_id')
        cal_KPI = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=2).select_related('objetivo','quienComenta_id')
        cal_CL = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=3).select_related('objetivo','quienComenta_id')
        cal_BONO = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=4).select_related('objetivo','quienComenta_id')
        cal_RESULTADOS = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=5).select_related('objetivo','quienComenta_id')

        empleados = Empleados.objects.filter(estatus=1)

        sumaOKR = datos_OKR.aggregate(total_okr=Sum('valor'))['total_okr']
        sumaKPI = datos_KPI.aggregate(total_kpi=Sum('valor'))['total_kpi']
        sumaCL = datos_CL.values_list('valor', flat=True).first()
        
        #obtener al empleado logueado
        usuario=1
        if request.user.is_authenticated:
            usuario= request.user.id
        usuario= Usuarios.objects.get(id=usuario)   
        empleado = Empleados.objects.get(no_emp=usuario.no_emp)
        #guardar en una variable el numero de empleado
        no_emp = empleado.no_emp
        departamento = empleado.departamento_id

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
            'cal_CL': list(cal_CL.values()),
            'empleados': list(empleados.values()),
            'departamento': departamento ,

        }
        return JsonResponse(data)


def obtener_datos_evaluacion_autoevaluacion(request):
    if request.method == 'GET':
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

@login_required
@user_passes_test(lambda u: u.departamento_id==11 or  u.departamento_id == 39 , login_url='/informacion/')
def calendario (request):
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    fechh = Fechas.objects.get(mes=mes, anio=año)
    calendarios = Calendario.objects.filter(fecha_id=fechh.id, tipo=1)
    fechas = Fechas.objects.filter(anio__gte=2025)
    ids_calendarios = calendarios.values_list('id', flat=True)
    todosCalendarios = Calendario.objects.filter(fecha_id__in=fechas, tipo=1)
    
    fech = meses(datetime.now())
    return render(request, 'calendario.html', {'calendarios': calendarios, 'todosCalendarios': todosCalendarios, 'fechas': fechas})

def obtenerFechas(calendarios):
    calendario = {
    }
    
    return calendario

def meses(fecha):
    #convertir la fecha a texto
    fech = fecha.strftime('%B')
    return fech


@login_required
@user_passes_test(lambda u: u.departamento_id==11 or  u.departamento_id == 39 , login_url='/informacion/')
def obtener_calendario(request):
    if request.method == 'GET':
        calendario_id = request.GET.get('calendario_id')
        
        calendario = Calendario.objects.get(id=calendario_id)
        calendario_json = serializers.serialize('json', [calendario])
        data = {
            'calendario': json.loads(calendario_json),
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
@user_passes_test(lambda u: u.departamento_id==11 or  u.departamento_id == 39 , login_url='/informacion/')
def guardarCalendario (request):
    comentariosInicialesInicio = (request.POST['comentariosInicialesInicio'])
    comentariosInicialesFin = request.POST['comentariosInicialesFin']
    empleadosInicio = request.POST['empleadosInicio']
    empleadosFin = request.POST['empleadosFin']
    gerentesInicio = request.POST['gerentesInicio']
    gerentesFin = request.POST['gerentesFin']
    jefesInicio = request.POST['evaluadoresInicio']
    jefesFin = request.POST['evaluadoresFin']
    tipo_seleccionado = request.POST.get('tipo', False) == 'on'
    fecha = int(request.POST['fechas'])
    fecha = Fechas.objects.get(id=fecha)
    
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    # fecha = Fechas.objects.get(mes=mes, anio=año)
    
    tipo=0
    
    #EL TIPO 1 ES EL CALENDARIO NORMAL DE TODOS
    #EL TIPO 2 ES EL CALENDARIO DEL AREA DE VENTAS
    
    if (tipo_seleccionado):
        tipo=2
    else :
        tipo=1
    
    #validar que no exista un calendario con la misma fecha
    try:
        calendario = Calendario.objects.get(tipo=tipo,fecha_id=fecha.id,)
    except: 
        calendario = Calendario (
            comentariosInicialesInicio=comentariosInicialesInicio,
            comentariosInicialesFin=comentariosInicialesFin,
            empleadosInicio=empleadosInicio,
            empleadosFin=empleadosFin,
            gerentesInicio=gerentesInicio,
            gerentesFin=gerentesFin,
            jefesInicio=jefesInicio,
            jefesFin=jefesFin,
            estatus=1,
            tipo=tipo,
            fecha_id=fecha.id
        )
        
        calendario.save()
    
        calendarioAgregado = Calendario.objects.get(tipo=tipo,fecha_id=fecha.id)
        
        calendarioF = CalendarioFijo (
                comentariosInicialesInicio=comentariosInicialesInicio,
                comentariosInicialesFin=comentariosInicialesFin,
                empleadosInicio=empleadosInicio,
                empleadosFin=empleadosFin,
                gerentesInicio=gerentesInicio,
                gerentesFin=gerentesFin,
                jefesInicio=jefesInicio,
                jefesFin=jefesFin,
                status=1,
                tipo=tipo,
                fecha_id=fecha.id,
                calendario_id=calendarioAgregado.id
        )
        
        calendarioF.save()
        
    return redirect(reverse('calendario'))

@login_required
@user_passes_test(lambda u: u.departamento_id==11 or  u.departamento_id == 39 , login_url='/informacion/')
def editarCalendario (request):
    comentariosInicialesInicio = (request.POST['comentariosInicialesInicioEditar'])
    comentariosInicialesFin = request.POST['comentariosInicialesFinEditar']
    empleadosInicio = request.POST['empleadosInicioEditar']
    empleadosFin = request.POST['empleadosFinEditar']
    gerentesInicio = request.POST['gerentesInicioEditar']
    gerentesFin = request.POST['gerentesFinEditar']
    jefesInicio = request.POST['evaluadoresInicioEditar']
    jefesFin = request.POST['evaluadoresFinEditar']
    tipo_seleccionado = request.POST.get('tipoEditar', False) == 'on'
    calendarioSeleccionado = request.POST['calendarioSelect']
    fecha = Fechas.objects.latest('id')
    tipo=0
    
    #EL TIPO 1 ES EL CALENDARIO NORMAL DE TODOS
    #EL TIPO 2 ES EL CALENDARIO DEL AREA DE VENTAS
    
    if (tipo_seleccionado):
        tipo=2
    else :
        tipo=1
    
    #validar que no exista un calendario con la misma fecha
    try:
        calendario = Calendario.objects.get(id=calendarioSeleccionado)
        calendario.comentariosInicialesInicio=comentariosInicialesInicio
        calendario.comentariosInicialesFin=comentariosInicialesFin
        calendario.empleadosInicio=empleadosInicio
        calendario.empleadosFin=empleadosFin
        calendario.gerentesInicio=gerentesInicio
        calendario.gerentesFin=gerentesFin
        calendario.jefesInicio=jefesInicio
        calendario.jefesFin=jefesFin
        calendario.save()
    except: 
       print("error")
        
    return redirect(reverse('calendario'))

@login_required
def informacion(request):
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp
    
    
    #empleado logueado
    empleado= Empleados.objects.get(no_emp=no_emp)
    return render(request, 'informacion.html', {'empleado': empleado})


@login_required
@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.rango_id == 6 , login_url='/informacion/')
def porEvaluar(request):
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleado= Empleados.objects.get(no_emp=no_emp)
    #checar donde el seguimiento sea igual al empleado logueado y si es evaluador 1 significa que puede poner comentarios, esa consulta me va a regresar varios
    #por que puede que el evaluador este varias veces en la tabla de seguimiento como evaluasor 1
    #AQUI DEBO DE CHECAR QUE COINCIDA CON LA FECHA QUE CAPITAL HUMANO INDIQUE QUE SE DEBE DE EVALUAR
    #MOSTRAR SOLO CUANOD ES JEFE LA DE EVALUADOR_1 Y CUANDO ES GERENTE MOSTRAR EVALUADOR_2 DEPENDE DE LAS FECHAS DE CAPITAL HUMANO DE CUAL Y CUAL MOSTRARE
    
    error=0
    
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    fechh = Fechas.objects.get(mes=mes, anio=año)
    evaSegui = []
    
    permisosTodos = 0
    permisosJefesTodos= 0
    permisosGerentesTodos =0 
    
    # #acalendario de ventas esta vigente y que apartado si el de jefes o gerentes
    # try:
    #     calendario = Calendario.objects.get(fecha_id=fechh.id,tipo=2)
    #     if (calendario.jefesInicio <= datetime.now().date() and calendario.jefesFin >= datetime.now().date() and  calendario.gerentesInicio <= datetime.now().date() and calendario.gerentesFin >= datetime.now().date()):
    #         permisosJefesVentas= 1
    #         permisosGerentesVentas= 1
    #         permisosVentas= 1
    #     else:
    #         if (calendario.jefesInicio <= datetime.now().date() and calendario.jefesFin >= datetime.now().date() ):
    #                 permisosJefesVentas= 1
    #                 permisosVentas= 1
    #         if (calendario.gerentesInicio <= datetime.now().date() and calendario.gerentesFin >= datetime.now().date() ):
    #             permisosGerentesVentas= 1
    #             permisosVentas= 1
    # except:
    #     error=4

    #calendario de todos esta vigente y que apartado si el de jefes o gerentes o ambos
    try:
        calendario = Calendario.objects.get(fecha_id=fechh.id,tipo=1)
        if (calendario.jefesInicio <= datetime.now().date() and calendario.jefesFin >= datetime.now().date() and  calendario.gerentesInicio <= datetime.now().date() and calendario.gerentesFin >= datetime.now().date()):
            permisosJefesTodos= 1
            permisosGerentesTodos= 1
            permisosTodos = 1
        else:
            if (calendario.jefesInicio <= datetime.now().date() and calendario.jefesFin >= datetime.now().date()):
                permisosJefesTodos= 1
                permisosTodos = 1
            if (calendario.gerentesInicio <= datetime.now().date() and calendario.gerentesFin >= datetime.now().date()):                
                permisosGerentesTodos= 1
                permisosTodos = 1  
    except:
        error=4
        
       
    
    evaSegui = []
    error=0
                
    if (empleado.departamento_id in (1,2,3,4,5,6,7,8,9,10,12,13,11,25,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48)):
        if (permisosTodos==1):
            if (permisosJefesTodos==1 and permisosGerentesTodos==1):
                try:
                    seguimientos = Rutas.objects.filter(evaluador_id=empleado.no_emp)
                    for segui in seguimientos:
                        evaluaciones = EvaluacionesAreas.objects.filter(ruta_id=segui.id, estado_id__in=[1, 2,5], fecha_id=fechh.id)
                        evaSegui.extend(evaluaciones)
                except:
                    error=3
            else:
                if (permisosJefesTodos==1):
                    try:
                        seguimientos = Rutas.objects.filter(evaluador_id=empleado.no_emp)
                        for segui in seguimientos:
                            empleados = Empleados.objects.exclude(rango_id=6)
                            evaluaciones = EvaluacionesAreas.objects.filter(ruta_id=segui.id, estado_id__in=[1, 2,5], fecha_id=fechh.id, empleado_id__in=empleados.values_list('no_emp', flat=True))
                            evaSegui.extend(evaluaciones)
                    except:
                        error=3
                else:
                    if (permisosGerentesTodos==1):
                        try:
                            seguimientos = Rutas.objects.filter(evaluador_id=empleado.no_emp)
                            for segui in seguimientos:
                                empleados = Empleados.objects.filter(rango_id=6)
                                evaluaciones = EvaluacionesAreas.objects.filter(ruta_id=segui.id, estado_id__in=[1, 2,5], fecha_id=fechh.id, empleado_id__in=empleados.values_list('no_emp', flat=True))
                                evaSegui.extend(evaluaciones)
                        except:
                            error=4
                    else:
                        error=1
     
    context ={
        "evaSegui": evaSegui,
        "empleado": empleado,
        "error": error,
    }
    return render(request, 'porEvaluar.html', context)

#validad como proteger esta vista
@login_required
def personaEvaluar (request):
    numeroEvaluacion_id = int(request.POST['numeroEvaluacion'])
    evaluacion = EvaluacionesAreas.objects.get(id=numeroEvaluacion_id)
    empleado = Empleados.objects.get(estatus=1, no_emp=evaluacion.empleado_id)
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleadoLogueado= Empleados.objects.get(no_emp=no_emp)
    
    #Es para saber si la autoevaluacion ya fue contestada o no
    seguimiento= Rutas.objects.get(id=evaluacion.ruta_id)
    # comentariosGenerales = ComentariosGenerales.objects.get(evaluacion_id=evaluacion.id)
    # resultados = CalificacionesGenerales.objects.get(evaluacion_id=evaluacion.id)
    obj = Areas.objects.filter(tipoEvaluacion_id=evaluacion.tipoEvaluacion_id)
    obj = Areas.objects.filter(tipoEvaluacion_id=evaluacion.tipoEvaluacion_id).prefetch_related('comentariosareas_set', 'calificacionesareas_set','porcentajes_set')

    for area in obj:
        area.tiene_calificacion = area.calificacionesareas_set.filter(evaluacion_id=evaluacion.id).exists()


    sumAreas = obj.filter(apartado_id=6).aggregate(total_areas=Sum('valor'))['total_areas']
    sumCL = obj.filter(apartado_id=7).values_list('valor', flat=True).first()
    sumCalidad = obj.filter(apartado_id=8).values_list('valor', flat=True).first()
            

    context ={
        "evaluacion": evaluacion,
        "obj": obj,
        "empleado": empleado,
        "sumAreas": sumAreas,
        "sumCL": sumCL,
        "sumCalidad": sumCalidad,
        "seguimiento": seguimiento,
        "empleado": empleado,
        "empleadoLogueado": empleadoLogueado,
    }
    
    return render(request, 'personaEvaluar.html', context)


def guardarCalificacion(request):
    if request.method == 'POST':
        comentarios = json.loads(request.POST.get('comentarios'))
        comentariosGenerales = json.loads(request.POST.get('comentariosGenerales'))
        respuestas = json.loads(request.POST.get('respuestas'))
        numEva = request.POST.get('numeroEvaluacion')
        total = request.POST.get('total')
        usuarioLogueado = request.POST.get('usuarioLogueado')
        #Traer la evaluacion de mi base de datos
        
        
        
        evaluacion = EvaluacionesAreas.objects.get(id=numEva)
        
        #obtener al empleado logueado
        usuario=1
        if request.user.is_authenticated:
            usuario= request.user.id
        usuario= Usuarios.objects.get(id=usuario)   
        empleado = Empleados.objects.get(no_emp=usuario.no_emp)
        #guardar en una variable el numero de empleado
        no_emp = empleado.no_emp
        #ESTO SI SIRVEEEEEEEEEEEEEEEEEEEEE, SOLO LO PUSE EN COMENTARIOS MIENTRAS HAGO LAS PRUEBAS DE LOS CORREOS
        #guardar los comentarios por cada objetivo
        
        #si sirve estoo
        for item in comentarios:
            comentariosObjetivos = ComentariosAreas(
                comentario= item['comentario'],
                area_id= item['id'],
                fechaComentario = datetime.now(),
                fecha_id = evaluacion.fecha_id,
                evaluacion_id = evaluacion.id,
                estatus=1,
            )
            comentariosObjetivos.save()
        
        
        seguimiento = Rutas.objects.get(id=evaluacion.ruta_id)
        
        code=0
        
        if seguimiento.evaluador_id == no_emp:
            #entro aqui por que el evaluador1_id es igual al empleado logueado
            resultadoGeneral= CalificacionesGenerales(
                calificacion_evaluador = total,
                estatus = 1,
                evaluacion_id = evaluacion.id,
            )
            resultadoGeneral.save()
            
        if len(comentariosGenerales) != 0:
            comentario=ComentariosGenerales(
            comentario_evaluador = comentariosGenerales[0]['comentario'],
            comentario_director="",
            comentario_capitalHumano="",
            comentario_calidad="",
            logros = "",
            estatus=1,
            evaluacion_id = evaluacion.id,
        )
            comentario.save()
        
        #el siguiente evaluador es 1 por eso finaliza la evaluacion
        evaluacion.estado_id = 3
        evaluacion.estatus = 3
        code=1
        evaluacion.save()
        
                
        #SI SIRVEEEEE
        for item in respuestas:
            if item['id'] != "-3":
                if CalificacionesAreas.objects.filter(area_id=item['id'], evaluacion_id=evaluacion.id).exists():
                    # Si ya existe una calificación para esta área, actualízala
                    respuesta = CalificacionesAreas.objects.get(area_id=item['id'], evaluacion_id=evaluacion.id)
                    respuesta.calificacion = item['respuesta']
                    respuesta.fechaCalificacion = datetime.now()
                    respuesta.save()
                else:    
                    respuesta = CalificacionesAreas(
                        calificacion = item['respuesta'],
                        fechaCalificacion = datetime.now(),
                        estatus = 1,
                        fecha_id = evaluacion.fecha_id,
                        area_id= item['id'],
                        evaluacion_id = evaluacion.id
                    )
                    respuesta.save()
        return JsonResponse({'message': 'Comentarios guardados exitosamente', 'code': code})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    
def guardarAvance(request):
    if request.method == 'POST':
        comentarios = json.loads(request.POST.get('comentarios'))
        comentariosGenerales = json.loads(request.POST.get('comentariosGenerales'))
        respuestas = json.loads(request.POST.get('respuestas'))
        numEva = request.POST.get('numeroEvaluacion')
        total = request.POST.get('total')
        usuarioLogueado = request.POST.get('usuarioLogueado')
        #Traer la evaluacion de mi base de datos
        
        
        
        evaluacion = EvaluacionesAreas.objects.get(id=numEva)
        
        #obtener al empleado logueado
        usuario=1
        if request.user.is_authenticated:
            usuario= request.user.id
        usuario= Usuarios.objects.get(id=usuario)   
        empleado = Empleados.objects.get(no_emp=usuario.no_emp)
        #guardar en una variable el numero de empleado
        no_emp = empleado.no_emp
        #ESTO SI SIRVEEEEEEEEEEEEEEEEEEEEE, SOLO LO PUSE EN COMENTARIOS MIENTRAS HAGO LAS PRUEBAS DE LOS CORREOS
        #guardar los comentarios por cada objetivo
        
        #si sirve estoo
        for item in comentarios:
            comentariosObjetivos = ComentariosAreas(
                comentario= item['comentario'],
                area_id= item['id'],
                fechaComentario = datetime.now(),
                fecha_id = evaluacion.fecha_id,
                evaluacion_id = evaluacion.id,
                estatus=1,
            )
            comentariosObjetivos.save()
        
        
        seguimiento = Rutas.objects.get(id=evaluacion.ruta_id)
        
        code=0
        
        # NO GUARDA CALIFICACION FINAAAAL 
        # if seguimiento.evaluador_id == no_emp:
        #     #entro aqui por que el evaluador1_id es igual al empleado logueado
        #     resultadoGeneral= CalificacionesGenerales(
        #         calificacion_evaluador = total,
        #         estatus = 1,
        #         evaluacion_id = evaluacion.id,
        #     )
        #     resultadoGeneral.save()
            
        if len(comentariosGenerales) != 0:
            comentario=ComentariosGenerales(
            comentario_evaluador = comentariosGenerales[0]['comentario'],
            comentario_director="",
            comentario_capitalHumano="",
            comentario_calidad="",
            logros = "",
            estatus=1,
            evaluacion_id = evaluacion.id,
        )
            comentario.save()
        
        #Lo dejo asi por que es pendiente o sea guarda info pero no toda y la deja pendiente
        evaluacion.estado_id = 5
        evaluacion.estatus = 5
        code=1
        evaluacion.save()
        
        #SI SIRVEEEEE
        for item in respuestas:
            if item['id'] != "-3":
                
                if CalificacionesAreas.objects.filter(area_id=item['id'], evaluacion_id=evaluacion.id).exists():
                    # Si ya existe una calificación para esta área, actualízala
                    respuesta = CalificacionesAreas.objects.get(area_id=item['id'], evaluacion_id=evaluacion.id)
                    respuesta.calificacion = item['respuesta']
                    respuesta.fechaCalificacion = datetime.now()
                    respuesta.save()
                else:    
                    respuesta = CalificacionesAreas(
                        calificacion = item['respuesta'],
                        fechaCalificacion = datetime.now(),
                        estatus = 1,
                        fecha_id = evaluacion.fecha_id,
                        area_id= item['id'],
                        evaluacion_id = evaluacion.id
                    )
                    respuesta.save()
                
                
        return JsonResponse({'message': 'Comentarios guardados exitosamente', 'code': code})
    else:
        # Manejar el caso en que la solicitud no sea POST
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
@login_required
def reportesEmpleado (request):
    #obtener al empleado logueado
    usuario=1
    if request.user.is_authenticated:
        usuario= request.user.id
    usuario= Usuarios.objects.get(id=usuario)   
    empleado = Empleados.objects.get(no_emp=usuario.no_emp)
    
    fechaActual = datetime.now()
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    fechh = Fechas.objects.get(mes=mes, anio=año)
    evaluaciones = EvaluacionesAreas.objects.filter(
    empleado_id=empleado.no_emp,
    fecha_id__lte=fechh.id
    )
    
    # Si es 0 significa que no hay evaluaciones en el anterior sistema
    
    anteriorSistema = 0
    try :
        evaluacionesAnteriores = EvaluacionesAntiguos.objects.using('mysql_db').filter(no_emp=empleado.no_emp, anio_evaluacion=2024)
        anteriorSistema = 1
    except:
        evaluacionesAnteriores = []
        anteriorSistema = 0
    
    fechas = Fechas.objects.all()
    
    context ={
        "empleado": empleado,
        "evaluaciones": evaluaciones,
        "evaluacionesAnteriores": evaluacionesAnteriores,
        "anteriorSistema": anteriorSistema,
        "fechas": fechas,
    }
    
    return render(request, 'reportesEmpleado.html', context)

@login_required
def obtener_reporte_empleados(request):
    if request.method == 'GET':
        evaluacion_id = request.GET.get('evaluacion_id')
        # Convierte el ID de la evaluación a entero
        evaluacion_id = int(evaluacion_id)
        evaluacion= Evaluaciones.objects.get(id=evaluacion_id)
        evaluacion_id = evaluacion.numeroEvaluacion_id
        

        evaluaciones= NumerosEvaluaciones.objects.get(id=evaluacion_id)
        
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
        
        cal_OKR = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=1).select_related('objetivo','quienComenta_id')
        cal_KPI = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=2).select_related('objetivo','quienComenta_id')
        cal_CL = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=3).select_related('objetivo','quienComenta_id')
        cal_BONO = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=4).select_related('objetivo','quienComenta_id')
        cal_RESULTADOS = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=5).select_related('objetivo','quienComenta_id')
        

        empleados = Empleados.objects.filter(estatus=1)

        sumaOKR = datos_OKR.aggregate(total_okr=Sum('valor'))['total_okr']
        sumaKPI = datos_KPI.aggregate(total_kpi=Sum('valor'))['total_kpi']
        sumaCL = datos_CL.values_list('valor', flat=True).first()
        
        evaluacion_id = request.GET.get('evaluacion_id')
        seguimiento = Seguimiento.objects.get(id=evaluacion.seguimiento_id)
        evaluacion= Evaluaciones.objects.get(id=evaluacion_id)
        empleado = Empleados.objects.get(no_emp=evaluacion.empleado_id)
        
        
        try:
            calificaciones = Resultados.objects.get(evaluacion_id=evaluacion.id)
            calificacionAutoevaluado = calificaciones.calificacion_autoevaluado
            e1_calificacion = calificaciones.calificacion_evaluador1
            e2_calificacion = calificaciones.calificacion_evaluador2
            e3_calificacion = calificaciones.calificacion_evaluador3
            e4_calificacion = calificaciones.calificacion_evaluador4
        except:
            calificacionAutoevaluado=0
            e1_calificacion = 0
            e2_calificacion = 0
            e3_calificacion = 0
            e4_calificacion = 0
        try:    
            comentarios = Comentarios.objects.get(evaluacion_id=evaluacion.id)
            comentario_autoevaluado=comentarios.comentario_autoevaluado
            comentario_evaluador1=comentarios.comentario_evaluador1
            comentario_evaluador2=comentarios.comentario_evaluador2
            comentario_evaluador3=comentarios.comentario_evaluador3
            comentario_evaluador4=comentarios.comentario_evaluador4
            logros=comentarios.logros
            comentario_capitalHumano=comentarios.comentario_capitalHumano
            comentario_calidad=comentarios.comentario_calidad
            comentario_director=comentarios.comentario_director
        except:
            comentarios = []
            comentario_autoevaluado=""
            comentario_evaluador1=""
            comentario_evaluador2=""
            comentario_evaluador3=""
            comentario_evaluador4=""
            logros=""
            comentario_capitalHumano=""
            comentario_calidad=""
            comentario_director=""
            
        
        #DATOS EMPLEADO
        fecha = Fechas.objects.get(id=evaluacion.fecha_id)
        no_emp = evaluacion.empleado_id
        nombre = empleado.nombre + " " + empleado.apellido_paterno + " " + empleado.apellido_materno
        puesto = empleado.puesto.nombre
        periodo = fechaMes(fecha.mes, fecha.anio)
        etapa = evaluacion.fase.nombre
        
        
        #DATOS EVALUADOR 1
        evaluador1 = Empleados.objects.get(no_emp=seguimiento.evaluador1_id)
        e1_no_Emp = evaluador1.no_emp
        e1_nombre = evaluador1.nombre + " " + evaluador1.apellido_paterno + " " + evaluador1.apellido_materno
        e1_puesto = evaluador1.puesto.nombre
        
        #DATOS EVALUADOR 2
        evaluador2 = Empleados.objects.get(no_emp=seguimiento.evaluador2_id)
        e2_no_Emp = evaluador2.no_emp
        e2_nombre = evaluador2.nombre + " " + evaluador2.apellido_paterno + " " + evaluador2.apellido_materno
        e2_puesto = evaluador2.puesto.nombre
    
        #DATOS EVALUADOR 3
        evaluador3 = Empleados.objects.get(no_emp=seguimiento.evaluador3_id)
        e3_no_Emp = evaluador3.no_emp
        e3_nombre = evaluador3.nombre + " " + evaluador3.apellido_paterno + " " + evaluador3.apellido_materno
        e3_puesto = evaluador3.puesto.nombre
        
        #DATOS EVALUADOR 4
        evaluador4 = Empleados.objects.get(no_emp=seguimiento.evaluador4_id)
        e4_no_Emp = evaluador4.no_emp
        e4_nombre = evaluador4.nombre + " " + evaluador4.apellido_paterno + " " + evaluador4.apellido_materno
        e4_puesto = evaluador4.puesto.nombre
                    
        
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
            'empleados': list(empleados.values()),
            'tipo': evaluaciones.estatus,
            'cal_OKR': list(cal_OKR.values()),
            'cal_KPI': list(cal_KPI.values()),
            'cal_CL': list(cal_CL.values()),
            'cal_BONO': list(cal_BONO.values()),
            'cal_RESULTADOS': list(cal_RESULTADOS.values()),
            'no_emp': no_emp,
            'nombre': nombre,
            'puesto': puesto,
            'periodo': periodo,
            'calificacionAutoevaluado': calificacionAutoevaluado,
            'etapa': etapa,
            'e1_no_Emp': e1_no_Emp,
            'e1_nombre': e1_nombre,
            'e1_puesto': e1_puesto,
            'e1_calificacion': e1_calificacion,
            'e2_no_Emp': e2_no_Emp,
            'e2_nombre': e2_nombre,
            'e2_puesto': e2_puesto,
            'e2_calificacion': e2_calificacion,
            'e3_no_Emp': e3_no_Emp,
            'e3_nombre': e3_nombre,
            'e3_puesto': e3_puesto,
            'e3_calificacion': e3_calificacion,
            'e4_no_Emp': e4_no_Emp,
            'e4_nombre': e4_nombre,
            'e4_puesto': e4_puesto,
            'e4_calificacion': e4_calificacion,
            'c_autoevaluado': comentario_autoevaluado,
            'c_evaluador1': comentario_evaluador1,
            'c_evaluador2': comentario_evaluador2,
            'c_evaluador3': comentario_evaluador3,
            'c_evaluador4': comentario_evaluador4,
            'logros': logros,
            'c_capitalHumano': comentario_capitalHumano,
            'c_calidad': comentario_calidad,
            'c_director': comentario_director,
        }
        return JsonResponse(data)


#No lo ocupo hasta el momento
def fechaMes (mes, anio):
    fecha=""
    if (mes == 1):
        fecha = "Diciembre" + " " + str(anio)
    elif (mes == 2):
        fecha = "Enero" + " " + str(anio)
    elif (mes == 3):
        fecha = "Febrero" + " " + str(anio)
    elif (mes == 4):
        fecha = "Marzo" + " " + str(anio)
    elif (mes == 5):
        fecha = "Abril" + " " + str(anio)
    elif (mes == 6):
        fecha = "Mayo" + " " + str(anio)
    elif (mes == 7):
        fecha = "Junio" + " " + str(anio)
    elif (mes == 8):
        fecha = "Julio" + " " + str(anio)
    elif (mes == 9):
        fecha = "Agosto" + " " + str(anio)
    elif (mes == 10):
        fecha = "Septiembre" + " " + str(anio)
    elif (mes == 11):
        fecha = "Octubre" + " " + str(anio)
    elif (mes == 12):
        fecha = "Noviembre" + " " + str(anio)
    else:
        fecha = "Error"
    return fecha

def generarEva():
    fechaActual = datetime.now()
    fecha = Fechas.objects.latest('id')
    dia = fechaActual.day
    mes = fechaActual.month
    año = fechaActual.year
    mes = mes + 1
    try :
        #Si encuentra la fecha de un mes mas echa ya no la hace
        fecha = Fechas.objects.get(mes=mes, anio=año)
    except:
        #Si no encuentra la fecha de este mes la crea y sus evaluaciones y comentarios
        #para hacerlo cada mes solo cambiar la variable dia por mes, esto solo es de practica
        if(mes != fecha.mes or año != fecha.anio):
            fechaAnterior = Fechas.objects.latest('id')
            fecha = Fechas(
                mes = mes,
                anio = año,
                version = fecha.version + 1
            )
            fecha.save()
            evaluacionesAnteriores = EvaluacionesAreas.objects.filter(fecha_id=fechaAnterior.id)
            fechaNueva = Fechas.objects.latest('id')
            for evaluacion in evaluacionesAnteriores:
                #aqui validar que estatus tiene el empleado y si es 0 no se agrega una evaluacion
                empleado = Empleados.objects.get(no_emp=evaluacion.empleado_id)
                if empleado.estatus == 1:
                    ev = EvaluacionesAreas (
                        fecha_id = fechaNueva.id,
                        empleado_id = evaluacion.empleado_id,
                        estatus = 1,
                        tipoEvaluacion_id = evaluacion.tipoEvaluacion_id,
                        ruta_id = evaluacion.ruta_id,
                        estado_id = 1
                    )
                    ev.save()
                    # eva = Evaluaciones.objects.latest('id')
                    # comentarios = Comentarios(
                    #     evaluacion_id=eva.id,
                    #     comentario_autoevaluado="",
                    #     comentario_evaluador1="",
                    #     comentario_evaluador2="",
                    #     comentario_evaluador3="",
                    #     comentario_evaluador4="",
                    #     comentario_capitalHumano="",
                    #     comentario_director="",
                    #     logros="",
                    #     estatus=1
                    # )
                    # comentarios.save()


def crearEvaluaciones(request):
    generarEva()
    return redirect(reverse('evaluaciones'))


@login_required
@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def reportesGenerales (request):
    #usuario logueado
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleado= Empleados.objects.get(no_emp=no_emp)
    
    if (empleado.departamento_id == 11 or empleado.no_emp == 101):
        empleados = Empleados.objects.filter(estatus=1).order_by('nombre')
    else:
        seguimientos = Seguimiento.objects.filter(Q(evaluador1_id=empleado.no_emp) | Q(evaluador2_id=empleado.no_emp) | Q(evaluador3_id=empleado.no_emp) | Q(evaluador4_id=empleado.no_emp))
        evaluaciones = Evaluaciones.objects.filter(seguimiento_id__in=seguimientos).values('empleado_id','seguimiento_id').distinct()
        
        rutas = Rutas.objects.filter(evaluador_id=empleado.no_emp)
        evaluacionesAreas = EvaluacionesAreas.objects.filter(ruta_id__in=rutas).values('empleado_id','ruta_id').distinct()
        
        #empleados = Empleados.objects.filter(estatus=1, no_emp__in=evaluaciones.values('empleado_id')).order_by('nombre')
        empleados = Empleados.objects.filter(estatus=1, no_emp__in=evaluacionesAreas.values('empleado_id')).order_by('nombre')
    
    departamentos = Departamentos.objects.filter(estatus=1)
    anios = Fechas.objects.values('anio').distinct()
    fechas = Fechas.objects.all()
    fechas_json = serializers.serialize('json', fechas)
    
    
    context ={
        "departamentos": departamentos,
        "empleados": empleados,
        "anios": anios,
        "fechas": fechas,
        "fechas_json": fechas_json,
        "empleado": empleado,
    }
    return render(request, 'reportesGenerales.html', context)


@login_required
@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.departamento_id == 11 or  u.departamento_id == 39, login_url='/informacion/')
def generarReporte(request):
    if request.method == 'POST':
        try:
            # Obtener los datos de los arreglos desde el formulario
            camposSeleccionados_str = request.POST.get('camposSeleccionados')
            empleadosSeleccionados_str = request.POST.get('empleadosSeleccionados')
            departamentosSeleccionados_str = request.POST.get('departamentosSeleccionados')
            mesesSeleccionados_str = request.POST.get('mesesSeleccionados')
            
            # Convertir las cadenas JSON a diccionarios
            camposSeleccionados = json.loads(camposSeleccionados_str)
            empleadosSeleccionados = json.loads(empleadosSeleccionados_str)
            departamentosSeleccionados = json.loads(departamentosSeleccionados_str)
            mesesSeleccionados = json.loads(mesesSeleccionados_str)
            seguimiento = Seguimiento.objects.all()
            
            if (len(empleadosSeleccionados) == 0 and len(departamentosSeleccionados) == 0 and len(mesesSeleccionados) == 0):
                datos = Evaluaciones.objects.all().select_related('empleado', 'fecha', 'numeroEvaluacion', 'seguimiento', 'fase')
                calificaciones = Resultados.objects.filter(evaluacion_id__in=datos).select_related('evaluacion')
                comentarios = Comentarios.objects.filter(evaluacion_id__in=datos)
                
                datosareas = EvaluacionesAreas.objects.all().select_related('empleado', 'fecha', 'tipoEvaluacion', 'ruta', 'estado')
                calificacionesAreas = CalificacionesGenerales.objects.filter(evaluacion_id__in=datosareas).select_related('evaluacion')
                comentariosAreas = ComentariosGenerales.objects.filter(evaluacion_id__in=datosareas)
                
                try:
                    cal_BONO = CalificacionesObjetivos.objects.filter(evaluacion_id_in=datos, objetivo__apartado_id=4).select_related('objetivo','quienComenta_id')
                    bonos = []
                    bonosJ = []
                    for dat in datos:
                        evaluador1 = []
                        for seg in seguimiento:
                            if seg.id == dat.seguimiento_id:
                                evaluador1 = seg.evaluador1_id
                        sumEmp=0
                        sumJef=0
                        for cal in calificaciones_objetivos:
                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == dat.empleado_id:
                              sumEmp += cal.calificacion
                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == evaluador1:
                              sumJef += cal.calificacion
                        bonos.append([dat.id,sumEmp])
                        bonosJ.append([dat.id,sumJef])
                except:
                    cal_BONO = []
                    bonos = []
                    bonosJ = []
                try:
                    calificaciones_objetivos = CalificacionesObjetivos.objects.filter(evaluacion_id__in=datos, objetivo__apartado_id=4).select_related('objetivo')
                    bonos = []
                    bonosJ = []
                    for dat in datos:
                        evaluador1 = []
                        for seg in seguimiento:
                            if seg.id == dat.seguimiento_id:
                                evaluador1 = seg.evaluador1_id
                        sumEmp=0
                        sumJef=0
                        for cal in calificaciones_objetivos:
                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == dat.empleado_id:
                              sumEmp += cal.calificacion
                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == evaluador1:
                              sumJef += cal.calificacion
                        bonos.append([dat.id,sumEmp])
                        bonosJ.append([dat.id,sumJef])
                except:
                    calificaciones_objetivos = []
                    bonos = []
                    bonosJ = []
                
            else:
                if (len(empleadosSeleccionados) != 0 and len(mesesSeleccionados) == 0):
                    datos = Evaluaciones.objects.filter(empleado_id__in=empleadosSeleccionados).select_related('empleado', 'fecha', 'numeroEvaluacion', 'seguimiento', 'fase')
                    calificaciones = Resultados.objects.filter(evaluacion_id__in=datos).select_related('evaluacion')
                    comentarios = Comentarios.objects.filter(evaluacion_id__in=datos)
                    calificaciones_objetivos = CalificacionesObjetivos.objects.filter(evaluacion_id__in=datos, objetivo__apartado_id=4).select_related('objetivo')
                    
                    datosareas = EvaluacionesAreas.objects.filter(empleado_id__in=empleadosSeleccionados).select_related('empleado', 'fecha', 'tipoEvaluacion', 'ruta', 'estado')
                    calificacionesAreas = CalificacionesGenerales.objects.filter(evaluacion_id__in=datosareas).select_related('evaluacion')
                    comentariosAreas = ComentariosGenerales.objects.filter(evaluacion_id__in=datosareas)
                
                    bonos = []
                    bonosJ = []
                    for dat in datos:
                        evaluador1 = []
                        for seg in seguimiento:
                            if seg.id == dat.seguimiento_id:
                                evaluador1 = seg.evaluador1_id
                        sumEmp=0
                        sumJef=0
                        for cal in calificaciones_objetivos:
                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == dat.empleado_id:
                              sumEmp += cal.calificacion
                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == evaluador1:
                              sumJef += cal.calificacion
                        bonos.append([dat.id,sumEmp])
                        bonosJ.append([dat.id,sumJef])
                        
                else: 
                    if (len(empleadosSeleccionados) != 0 and len(mesesSeleccionados) != 0):
                        datos = Evaluaciones.objects.filter(empleado_id__in=empleadosSeleccionados, fecha_id__in=mesesSeleccionados).select_related('empleado', 'fecha', 'numeroEvaluacion', 'seguimiento', 'fase')
                        calificaciones = Resultados.objects.filter(evaluacion_id__in=datos).select_related('evaluacion')
                        comentarios = Comentarios.objects.filter(evaluacion_id__in=datos)
                        calificaciones_objetivos = CalificacionesObjetivos.objects.filter(evaluacion_id__in=datos, objetivo__apartado_id=4).select_related('objetivo')
                        
                        datosareas = EvaluacionesAreas.objects.filter(empleado_id__in=empleadosSeleccionados, fecha_id__in=mesesSeleccionados).select_related('empleado', 'fecha', 'tipoEvaluacion', 'ruta', 'estado')
                        calificacionesAreas = CalificacionesGenerales.objects.filter(evaluacion_id__in=datosareas).select_related('evaluacion')
                        comentariosAreas = ComentariosGenerales.objects.filter(evaluacion_id__in=datosareas)
                    
                        bonos = []
                        bonosJ = []
                        for dat in datos:
                            evaluador1 = 0
                            for seg in seguimiento:
                                if seg.id == dat.seguimiento_id:
                                    evaluador1 = seg.evaluador1_id
                                    
                            sumEmp=0
                            sumJef=0
                            for cal in calificaciones_objetivos:
                                if dat.id == cal.evaluacion_id and cal.quienCalifica_id == dat.empleado_id:
                                    sumEmp += cal.calificacion
                                if dat.id == cal.evaluacion_id and cal.quienCalifica_id == evaluador1:
                                    sumJef += cal.calificacion
                            bonos.append([dat.id,sumEmp])
                            bonosJ.append([dat.id,sumJef])
                    else:
                        if (len(departamentosSeleccionados) != 0 and len(mesesSeleccionados) == 0):
                            datos = Evaluaciones.objects.filter(empleado__departamento_id__in=departamentosSeleccionados).select_related('empleado', 'fecha', 'numeroEvaluacion', 'seguimiento', 'fase')
                            calificaciones = Resultados.objects.filter(evaluacion_id__in=datos).select_related('evaluacion')
                            comentarios = Comentarios.objects.filter(evaluacion_id__in=datos)
                            calificaciones_objetivos = CalificacionesObjetivos.objects.filter(evaluacion_id__in=datos, objetivo__apartado_id=4).select_related('objetivo')
                            datosareas = EvaluacionesAreas.objects.filter(empleado__departamento_id__in=departamentosSeleccionados).select_related('empleado', 'fecha', 'tipoEvaluacion', 'ruta', 'estado')
                            calificacionesAreas = CalificacionesGenerales.objects.filter(evaluacion_id__in=datosareas).select_related('evaluacion')
                            comentariosAreas = ComentariosGenerales.objects.filter(evaluacion_id__in=datosareas)
                        
                            bonos = []
                            bonosJ = []
                            for dat in datos:
                                evaluador1 = []
                                for seg in seguimiento:
                                    if seg.id == dat.seguimiento_id:
                                        evaluador1 = seg.evaluador1_id
                                sumEmp=0
                                sumJef=0
                                for cal in calificaciones_objetivos:
                                    if dat.id == cal.evaluacion_id and cal.quienCalifica_id == dat.empleado_id:
                                        sumEmp += cal.calificacion
                                    if dat.id == cal.evaluacion_id and cal.quienCalifica_id == evaluador1:
                                        sumJef += cal.calificacion
                                bonos.append([dat.id,sumEmp])
                                bonosJ.append([dat.id,sumJef])
                        else:
                            if (len(departamentosSeleccionados) != 0 and len(mesesSeleccionados) != 0):
                                datos = Evaluaciones.objects.filter(empleado__departamento_id__in=departamentosSeleccionados, fecha_id__in=mesesSeleccionados).select_related('empleado', 'fecha', 'numeroEvaluacion', 'seguimiento', 'fase')
                                calificaciones = Resultados.objects.filter(evaluacion_id__in=datos).select_related('evaluacion')
                                comentarios = Comentarios.objects.filter(evaluacion_id__in=datos)
                                calificaciones_objetivos = CalificacionesObjetivos.objects.filter(evaluacion_id__in=datos, objetivo__apartado_id=4).select_related('objetivo')
                                datosareas = EvaluacionesAreas.objects.filter(empleado__departamento_id__in=departamentosSeleccionados, fecha_id__in=mesesSeleccionados).select_related('empleado', 'fecha', 'tipoEvaluacion', 'ruta', 'estado')
                                calificacionesAreas = CalificacionesGenerales.objects.filter(evaluacion_id__in=datosareas).select_related('evaluacion')
                                comentariosAreas = ComentariosGenerales.objects.filter(evaluacion_id__in=datosareas)
                                bonos = []
                                bonosJ = []
                                for dat in datos:
                                    evaluador1 = []
                                    for seg in seguimiento:
                                        if seg.id == dat.seguimiento_id:
                                            evaluador1 = seg.evaluador1_id
                                    sumEmp=0
                                    sumJef=0
                                    for cal in calificaciones_objetivos:
                                        if dat.id == cal.evaluacion_id and cal.quienCalifica_id == dat.empleado_id:
                                            sumEmp += cal.calificacion
                                        if dat.id == cal.evaluacion_id and cal.quienCalifica_id == evaluador1:
                                            sumJef += cal.calificacion
                                    bonos.append([dat.id,sumEmp])
                                    bonosJ.append([dat.id,sumJef])
                            else:
                                if (len(empleadosSeleccionados) == 0 and len(departamentosSeleccionados) == 0 and len(mesesSeleccionados) != 0):
                                    datos = Evaluaciones.objects.filter(fecha_id__in=mesesSeleccionados).select_related('empleado', 'fecha', 'numeroEvaluacion', 'seguimiento', 'fase')
                                    calificaciones = Resultados.objects.filter(evaluacion_id__in=datos).select_related('evaluacion')
                                    comentarios = Comentarios.objects.filter(evaluacion_id__in=datos)
                                    calificaciones_objetivos = CalificacionesObjetivos.objects.filter(evaluacion_id__in=datos, objetivo__apartado_id=4).select_related('objetivo')
                                    datosareas = EvaluacionesAreas.objects.filter(fecha_id__in=mesesSeleccionados).select_related('empleado', 'fecha', 'tipoEvaluacion', 'ruta', 'estado')
                                    calificacionesAreas = CalificacionesGenerales.objects.filter(evaluacion_id__in=datosareas).select_related('evaluacion')
                                    comentariosAreas = ComentariosGenerales.objects.filter(evaluacion_id__in=datosareas)
                                    bonos = []
                                    bonosJ = []
                                    for dat in datos:
                                        evaluador1 = []
                                        for seg in seguimiento:
                                            if seg.id == dat.seguimiento_id:
                                                evaluador1 = seg.evaluador1_id
                                        sumEmp=0
                                        sumJef=0
                                        for cal in calificaciones_objetivos:
                                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == dat.empleado_id:
                                                sumEmp += cal.calificacion
                                            if dat.id == cal.evaluacion_id and cal.quienCalifica_id == evaluador1:
                                                sumJef += cal.calificacion
                                        bonos.append([dat.id,sumEmp])
                                        bonosJ.append([dat.id,sumJef])
                                else:
                                    datos = []
                                    calificaciones = []
                                    comentarios = []
                                    calificaciones_objetivos = []
                                    cal_BONO = []
                                    bonos = []
            
            no_emp = True
            nombre = True
            apellidos = False
            mes = False
            anio = False
            departamento = False
            autocalificacion = False
            evaluador1 = False
            evaluador2 = False
            evaluador3 = False
            evaluador4 = False
            director = False
            bempleado = False
            bjefe = False
            evaluadores = False
            comentariosGenerales = False
            
            for campos in camposSeleccionados:
                if campos == "no_emp":
                    no_emp = True
                if campos == "nombre":
                    nombre = True
                if campos == "apellido":
                    apellidos = True
                if campos == "mes":
                    mes = True
                if campos == "anio":
                    anio = True
                if campos == "departamento":
                    departamento = True
                if campos == "empleado":
                    autocalificacion = True
                if campos == "jefe":
                    evaluador1 = True
                if campos == "evaluador2":
                    evaluador2 = True
                if campos == "evaluador3":
                    evaluador3 = True
                if campos == "evaluador4":
                    evaluador4 = True
                if campos == "Director":
                    director = True
                if campos == "bonoE":
                    bempleado = True
                if campos == "bonoJ":
                    bjefe = True
                if campos == "evaluadores":
                    evaluadores = True
                if campos == "comentarios":
                    comentariosGenerales = True  
             
            # for bono in bonos:
            #     print("campo1:", bono[0], "campo2:", bono[1])
                  
            datos = Evaluaciones.objects.filter(id__in=[dat.id for dat in datos]).annotate(empleado_nombre=F('empleado__nombre')).order_by('empleado_nombre')      
            
            context = {
                'datos': datos,
                'calificaciones': calificaciones,
                'comentarios': comentarios,
                'calificaciones_objetivos': calificaciones_objetivos,
                'no_emp': no_emp,
                'nombre': nombre,
                'apellidos': apellidos,
                'mes': mes,
                'anio': anio,
                'departamento': departamento,
                'autocalificacion': autocalificacion,
                'evaluador1': evaluador1,
                'evaluador2': evaluador2,
                'evaluador3': evaluador3,
                'evaluador4': evaluador4,
                'director': director,
                'bempleado': bempleado,
                'bjefe': bjefe,
                'evaluadores': evaluadores,
                'comentariosGenerales': comentariosGenerales,
                'bonos': bonos,
                'bonosJ': bonosJ,
                'datosareas': datosareas,
                'calificacionesAreas': calificacionesAreas,
                'comentariosAreas': comentariosAreas
            }
            
            return render(request, 'reporte.html', context)
        except Exception as e:
            print(e)
            # Manejo de excepciones
    else:    
        return render(request, 'dashboard.html')
    
def reporte(request):
    return render(request, 'reporte.html')

@login_required
#@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.departamento_id == 11, login_url='/informacion/')
def reporteEvaluacion(request,id):
    numeroEvaluacion_id = id
    evaluacion = EvaluacionesAreas.objects.get(id=numeroEvaluacion_id)
    empleado = Empleados.objects.get(no_emp=evaluacion.empleado_id)
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleadoLogueado= Empleados.objects.get(no_emp=no_emp)
    #Checar que este dentro de la fecha que indique capital humano, si no que no pueda entrar, y el error sea 4 y muestre
    #un mensaje que diga que no puede entrar a la autoevaluacion por que no esta en la fecha indicada 
            
    tipo= evaluacion.tipoEvaluacion.estatus
    #Es para saber si la autoevaluacion ya fue contestada o no
    seguimiento= Rutas.objects.get(id=evaluacion.ruta_id)
    
    try:
        comentariosGenerales = ComentariosGenerales.objects.filter(evaluacion_id=evaluacion.id)
    except:
        comentariosGenerales = []
        
    obj = Areas.objects.filter(tipoEvaluacion_id=evaluacion.tipoEvaluacion_id)
    obj = Areas.objects.filter(tipoEvaluacion_id=evaluacion.tipoEvaluacion_id).prefetch_related('comentariosareas_set', 'calificacionesareas_set','porcentajes_set')
    
    cal_Areas = CalificacionesAreas.objects.filter(evaluacion_id=evaluacion.id, area__apartado_id=6)
    cal_CL = CalificacionesAreas.objects.filter(evaluacion_id=evaluacion.id, area__apartado_id=7)
    cal_Calidad = CalificacionesAreas.objects.filter(evaluacion_id=evaluacion.id, area__apartado_id=8)
    
    empleadoEvaluado = evaluacion.empleado_id
    
    suma_cal_Areas = 0
    for cal in cal_Areas:
        suma_cal_Areas = suma_cal_Areas + cal.calificacion
        
    suma_cal_CL = 0
    for cal in cal_CL:
        suma_cal_CL = suma_cal_CL + cal.calificacion
    
    suma_cal_calidad = 0
    for cal in cal_Calidad:
        suma_cal_calidad = suma_cal_calidad + cal.calificacion        
    try:
        resultados = CalificacionesGenerales.objects.get(evaluacion_id=evaluacion.id)
    except:
        resultados = []
    

    sumAreas = obj.filter(apartado_id=6).aggregate(total_areas=Sum('valor'))['total_areas']
    sumCL = obj.filter(apartado_id=7).values_list('valor', flat=True).first()
    sumCalidad=0
    try:
        sumCalidad = obj.filter(apartado_id=8).values_list('valor', flat=True).first()
    except:
        sumCalidad = 0       

    context ={
        "evaluacion": evaluacion,
        "obj": obj,
        "empleado": empleado,
        "sumAreas": sumAreas,
        'sumCL': sumCL,
        "sumCalidad": sumCalidad,
        "empleadoLogueado": empleadoLogueado,
        "comentariosGenerales": comentariosGenerales,
        "seguimiento": seguimiento,
        "tipo": tipo,
        "empleado": empleado,
        "empleadoLogueado": empleadoLogueado,
        "resultados": resultados,
        "suma_cal_Areas": suma_cal_Areas,
        "suma_cal_CL": suma_cal_CL,
        "suma_cal_calidad": suma_cal_calidad,
        "no_emp": no_emp,
    }
    return render(request, 'reporteEvaluacion.html',context)

@login_required
@user_passes_test(lambda u: u.no_emp == 101, login_url='/informacion/')
def guardarDirector(request):
    evaluacion_id = int(request.POST['evaluacion'])
    calificacion = int(request.POST['calificacionF'])
    comentario = request.POST['comentario']
        
    if calificacion != "":
        try:
            calificaciones = Resultados.objects.get(evaluacion_id=evaluacion_id)
            calificaciones.calificacion_director = calificacion
            calificaciones.save()
        except:
            calificaciones = Resultados (
                    calificacion_autoevaluado = -1,
                    calificacion_evaluador1 = -1,
                    calificacion_evaluador2 = -1,
                    calificacion_evaluador3 = -1,
                    calificacion_evaluador4 = -1,
                    calificacion_director = calificacion,
                    estatus = 1,
                    evaluacion_id = evaluacion_id
                )
            calificaciones .save()

    comentarios = Comentarios.objects.get(evaluacion_id=evaluacion_id)
    if comentario != "":
        comentario_director = comentarios.comentario_director + " -> " + comentario
        comentarios.comentario_director = comentario_director.strip()
        comentarios.save()
    
    return redirect(reverse('evaluaciones'))



@login_required
def obtener_reporte_empleados_antiguo(request):
    if request.method == 'GET':
        empleados = Empleado.objects.using('mysql_db').all()
        evaluacion_id = request.GET.get('evaluacion_id')
        # Convierte el ID de la evaluación a entero
        evaluacion_id = int(evaluacion_id)
        evaluacion = EvaluacionesAntiguos.objects.using('mysql_db').get(id_evaluaciones=evaluacion_id)
        empleado = Empleado.objects.using('mysql_db').get(no_emp=evaluacion.no_emp)
        jefe = Empleado.objects.using('mysql_db').get(no_emp=empleado.jefe_inmediato)
        ruta = RutaEvalua.objects.using('mysql_db').get(no_emp=evaluacion.no_emp)
        
        
        if ruta.segundo != 0:
            gerente = Empleado.objects.using('mysql_db').get(no_emp=ruta.segundo)
            e2_no_Emp = gerente.no_emp,
            e2_nombre = gerente.nom_emp,
            e2_puesto = gerente.puesto_emp,
            e2_calificacion = evaluacion.puntuacion_gerente,
        else:
            e2_no_Emp= 1,
            e2_nombre= "e2_nombre",
            e2_puesto= "e2_puesto",
            e2_calificacion=23,
            
        if ruta.tercero != 0 and ruta.tercero != 10000:
            tercer = Empleado.objects.using('mysql_db').get(no_emp=ruta.tercero)
            e3_no_Emp = tercer.no_emp,
            e3_nombre = tercer.nom_emp,
            e3_puesto = tercer.puesto_emp,
            e3_calificacion = 0,
        else :
            e3_no_Emp= 1,
            e3_nombre= "e3_nombre",
            e3_puesto= "e3_puesto",
            e3_calificacion= 0,
        
        
        # Obtener los valores únicos de id_apartado de la tabla ApartadosMes
        apartadosmMes_ids = ApartadosMes.objects.using('mysql_db').filter(
            no_emp=evaluacion.no_emp,
            año=evaluacion.anio_evaluacion,
            mes=evaluacion.mes_evaluacion
        ).values_list('id_apartado', flat=True).distinct()
        
        
        # for apartado in apartadosmMes_ids:
        #     print("apartadsso ", apartado)

        # Filtrar los registros en ApartadosAntiguos usando los valores únicos obtenidos
        apartados = ApartadosAntiguos.objects.using('mysql_db').filter(
            no_emp=evaluacion.no_emp,
            id_apartado__in=apartadosmMes_ids
        )
        
        for apartado in apartados:
            if (apartado.no_apartado==1):
                datos_OKR= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
                quejas_OKR = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_OKR.values('id_obj')))
                comet_OKR = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_OKR.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
                for dato in datos_OKR:
                    print("obj: ", dato.id_obj,"datos_OKR ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
                for comet in comet_OKR:
                    print("obj: ", comet.id_obj, "comet_OKR ", comet.comentarios_emp)
                    
            if (apartado.no_apartado==2):
                datos_KPI= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
                quejas_KPI = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_KPI.values('id_obj')))
                comet_KPI = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_KPI.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
                for dato in datos_KPI:
                    print("obj: ", dato.id_obj,"datos_KPI ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
                for comet in comet_KPI:
                    print("obj: ", comet.id_obj, "comet_KPI ", comet.comentarios_emp)
                    
            if (apartado.no_apartado==3):
                datos_CL= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
                quejas_CL = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_CL.values('id_obj')))
                comet_CL = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_CL.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
                for dato in datos_CL:
                    print("obj: ", dato.id_obj,"datos_CL ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
                for comet in comet_CL:
                    print("obj: ", comet.id_obj, "comet_CL ", comet.comentarios_emp)
            
            datos_BONO = []
            comet_BONO = []
                    
            if (apartado.no_apartado==4):
                datos_BONO= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
                quejas_BONO = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_BONO.values('id_obj')))
                comet_BONO = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_BONO.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
                for dato in datos_BONO:
                    print("obj: ", dato.id_obj,"datos_BONO ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
                for comet in comet_BONO:
                    print("obj: ", comet.id_obj, "comet_BONO ", comet.comentarios_emp)
                
            
            
        for apartado in apartadosmMes_ids:
            print("apartado ", apartado)

        if (datos_BONO == []):
            datos_BONO = list(datos_BONO)
            comet_BONO = list(comet_BONO)
        else:
            datos_BONO = list(datos_BONO.values())
            comet_BONO = list(comet_BONO.values())
        
        data = {
            'OKR': list(datos_OKR.values()),
            'coment_OKR': list(comet_OKR.values()),
            'KPI': list(datos_KPI.values()),
            'coment_KPI': list(comet_KPI.values()),
            'CL': list(datos_CL.values()),
            'coment_CL': list(comet_CL.values()),
            'BONO': datos_BONO,
            'coment_BONO': comet_BONO,
            'empleados': list(empleados.values()),
            'no_emp': empleado.no_emp,
            'nombre': empleado.nom_emp,
            'puesto': empleado.puesto_emp,
            'periodo': evaluacion.mes_evaluacion + " " + str(evaluacion.anio_evaluacion),
            'calificacionAutoevaluado': evaluacion.puntuacion_auto,
            'etapa': evaluacion.estatus,
            'e1_no_Emp': jefe.no_emp,
            'e1_nombre': jefe.nom_emp,
            'e1_puesto': jefe.puesto_emp,
            'e1_calificacion': evaluacion.puntuacion_total,
            'e2_no_Emp': e2_no_Emp,
            'e2_nombre': e2_nombre,
            'e2_puesto': e2_puesto,
            'e2_calificacion':e2_calificacion,
            'e3_no_Emp': e3_no_Emp,
            'e3_nombre': e3_nombre,
            'e3_puesto': e3_puesto,
            'e3_calificacion':e3_calificacion,
            'e4_no_Emp': 1,
            'e4_nombre': "e4_nombre",
            'e4_puesto': "e4_puesto",
            'e4_calificacion': 11,
            'c_autoevaluado': evaluacion.comen_compromisos,
            'c_evaluador1': evaluacion.comen_compromisos_jefe,
            'c_evaluador2': evaluacion.comen_compromisos_ger,
            'c_evaluador3': evaluacion.comen_compromisos_jefe_jefe,
            'c_evaluador4': evaluacion.comen_compromisos_adm,
            'logros': evaluacion.logro,
            'c_capitalHumano': "",
            'c_calidad': "",
            'c_director': evaluacion.comen_compromisos_dir,
        }
        return JsonResponse(data)
    
    
@login_required    
def obtenerEvaluacionAntigua(request,id):
    empleados = Empleado.objects.using('mysql_db').all()
    evaluacion_id = id
    # Convierte el ID de la evaluación a entero
    evaluacion_id = int(evaluacion_id)
    evaluacion = EvaluacionesAntiguos.objects.using('mysql_db').get(id_evaluaciones=evaluacion_id)
    empleado = Empleado.objects.using('mysql_db').get(no_emp=evaluacion.no_emp)
    jefe = Empleado.objects.using('mysql_db').get(no_emp=empleado.jefe_inmediato)
    ruta = RutaEvalua.objects.using('mysql_db').get(no_emp=evaluacion.no_emp)
        
        
    if ruta.segundo != 0:
        gerente = Empleado.objects.using('mysql_db').get(no_emp=ruta.segundo)
        e2_no_Emp = gerente.no_emp
        e2_nombre = gerente.nom_emp
        e2_puesto = gerente.puesto_emp
        e2_calificacion = evaluacion.puntuacion_gerente
    else:
        e2_no_Emp= 1
        e2_nombre= "e2_nombre"
        e2_puesto= "e2_puesto"
        e2_calificacion=23
    
    print ("gerente ", gerente)
    print ("e2_no_Emp ", e2_no_Emp)
    print ("e2_nombre ", e2_nombre)
    print ("e2_puesto ", e2_puesto)
    
            
    if ruta.tercero != 0 and ruta.tercero != 10000:
        tercer = Empleado.objects.using('mysql_db').get(no_emp=ruta.tercero)
        e3_no_Emp = tercer.no_emp
        e3_nombre = tercer.nom_emp
        e3_puesto = tercer.puesto_emp
        e3_calificacion = 0
        
    else :
        e3_no_Emp= 1
        e3_nombre= "e3_nombre"
        e3_puesto= "e3_puesto"
        e3_calificacion= 0
        
    print("mes: ", evaluacion.mes_evaluacion)
    print("año: ", evaluacion.anio_evaluacion)
        
    # Obtener los valores únicos de id_apartado de la tabla ApartadosMes
    apartadosmMes_ids = ApartadosMes.objects.using('mysql_db').filter(
        no_emp=evaluacion.no_emp,
        año=evaluacion.anio_evaluacion,
        mes=evaluacion.mes_evaluacion
    ).values_list('id_apartado', flat=True).distinct()
        
        
    for apartado in apartadosmMes_ids:
        print("apartadsso ", apartado)

    # Filtrar los registros en ApartadosAntiguos usando los valores únicos obtenidos
    apartados = ApartadosAntiguos.objects.using('mysql_db').filter(
        no_emp=evaluacion.no_emp,
        id_apartado__in=apartadosmMes_ids
    )
        
    for apartado in apartados:
        if (apartado.no_apartado==1):
            datos_OKR= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
            quejas_OKR = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_OKR.values('id_obj')))
            comet_OKR = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_OKR.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
            for dato in datos_OKR:
                print("obj: ", dato.id_obj,"datos_OKR ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
            for comet in comet_OKR:
                print("obj: ", comet.id_obj, "comet_OKR ", comet.comentarios_emp)
                    
        if (apartado.no_apartado==2):
            datos_KPI= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
            quejas_KPI = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_KPI.values('id_obj')))
            comet_KPI = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_KPI.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
            for dato in datos_KPI:
                print("obj: ", dato.id_obj,"datos_KPI ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
            for comet in comet_KPI:
                print("obj: ", comet.id_obj, "comet_KPI ", comet.comentarios_emp)
                    
        if (apartado.no_apartado==3):
            datos_CL= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
            quejas_CL = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_CL.values('id_obj')))
            comet_CL = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_CL.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
            for dato in datos_CL:
                print("obj: ", dato.id_obj,"datos_CL ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
            for comet in comet_CL:
                print("obj: ", comet.id_obj, "comet_CL ", comet.comentarios_emp)
            
            
        datos_BONO = []
        comet_BONO = []
                    
        if (apartado.no_apartado==4):
            datos_BONO= ObjetivosAntiguos.objects.using('mysql_db').filter(id_apartado=apartado.id_apartado)
            quejas_BONO = Quejas.objects.using('mysql_db').filter(id_objetivo__in=Subquery(datos_BONO.values('id_obj')))
            comet_BONO = Evaluaobjetivos.objects.using('mysql_db').filter(id_obj__in=Subquery(datos_BONO.values('id_obj')), mesevalua=evaluacion.mes_evaluacion, anioevalua=evaluacion.anio_evaluacion)                                                
            for dato in datos_BONO:
                print("obj: ", dato.id_obj,"datos_BONO ", dato.objetivo, "Mes: ", dato.mesevalua, "Año: ", dato.anio)
            for comet in comet_BONO:
                print("obj: ", comet.id_obj, "comet_BONO ", comet.comentarios_emp)
                
    for apartado in apartadosmMes_ids:
        print("apartado ", apartado)

    if (datos_BONO == []):
        datos_BONO = list(datos_BONO)
        comet_BONO = list(comet_BONO)
    else:
        datos_BONO = list(datos_BONO.values())
        comet_BONO = list(comet_BONO.values())
    hayBono = False
    if (datos_BONO != []):
        hayBono = True
        
    data = {
        'hayBono': hayBono,
        'OKR': list(datos_OKR.values()),
        'coment_OKR': list(comet_OKR.values()),
        'KPI': list(datos_KPI.values()),
        'coment_KPI': list(comet_KPI.values()),
        'CL': list(datos_CL.values()),
        'coment_CL': list(comet_CL.values()),
        'BONO': datos_BONO,
        'coment_BONO': comet_BONO,
        'empleados': list(empleados.values()),
        'no_emp': empleado.no_emp,
        'nombre': empleado.nom_emp,
        'puesto': empleado.puesto_emp,
        'periodo': evaluacion.mes_evaluacion + " " + str(evaluacion.anio_evaluacion),
        'calificacionAutoevaluado': evaluacion.puntuacion_auto,
        'etapa': evaluacion.estatus,
        'e1_no_Emp': jefe.no_emp,
        'e1_nombre': jefe.nom_emp,
        'e1_puesto': jefe.puesto_emp,
        'e1_calificacion': evaluacion.puntuacion_total,
        'e2_no_Emp': e2_no_Emp,
        'e2_nombre': e2_nombre,
        'e2_puesto': e2_puesto,
        'e2_calificacion':e2_calificacion,
        'e3_no_Emp': e3_no_Emp,
        'e3_nombre': e3_nombre,
        'e3_puesto': e3_puesto,
        'e3_calificacion':e3_calificacion,
        'e4_no_Emp': 1,
        'e4_nombre': "e4_nombre",
        'e4_puesto': "e4_puesto",
        'e4_calificacion': 11,
        'c_autoevaluado': evaluacion.comen_compromisos,
        'c_evaluador1': evaluacion.comen_compromisos_jefe,
        'c_evaluador2': evaluacion.comen_compromisos_ger,
        'c_evaluador3': evaluacion.comen_compromisos_jefe_jefe,
        'c_evaluador4': evaluacion.comen_compromisos_adm,
        'logros': evaluacion.logro,
        'c_capitalHumano': "",
        'c_calidad': "",
        'c_director': evaluacion.comen_compromisos_dir,
    } 
    return render(request, 'reporteEvaluacionAntiguo.html', data)

@login_required
def obtenerEvaluacionAreas(request,id):
    print("entra a obtener evaluacion areas")
    
    if request.user.is_authenticated:
          usuario= request.user.username
          
    print("usuario ", usuario)
    print("id ", id)
    no_emp = usuario
    evaluacion = EvaluacionesAreas.objects.get(fecha_id=id, empleado_id=no_emp)
    evid= evaluacion.id
    try:
        evaluacion = EvaluacionesAreas.objects.get(fecha_id=id, empleado_id=no_emp)
        evid= evaluacion.id
        print("evid ", evid)
        return redirect(reverse('reporteEvaluacion', args=[evid]))  # Corrección aquí
    except EvaluacionesAreas.DoesNotExist:
        # Manejar el caso en que la evaluación no exista
        #return redirect('/') 
        return redirect(reverse('reporteEvaluacion', args=[evid]))



@login_required
def obtenerEvaluacionOKR(request,id):
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.username
    
    no_emp = usuario
    evaluacion = Evaluaciones.objects.get(fecha_id=id,empleado_id=no_emp)
    evid= evaluacion.id
    return redirect(reverse('reporteEvaluacionOKR', args=[evid]))

@login_required
#@user_passes_test(lambda u: u.rango_id == 3 or u.rango_id == 1 or u.rango_id == 2 or u.rango_id == 5 or u.departamento_id == 11, login_url='/informacion/')
def reporteEvaluacionOKR(request,id):
    numeroEvaluacion_id = id
    evaluacion = Evaluaciones.objects.get(id=numeroEvaluacion_id)
    empleado = Empleados.objects.get(no_emp=evaluacion.empleado_id)
    usuario=1
    if request.user.is_authenticated:
          usuario= request.user.id

    usuario= Usuarios.objects.get(id=usuario)      
    no_emp = usuario.no_emp

    #empleado logueado
    empleadoLogueado= Empleados.objects.get(no_emp=no_emp)
    siHayBono = False
    siHayResultados = False
    idCL = 0
    objCL=""
    metCL=""
    valCL=""
    comentCL= []
    #Checar que este dentro de la fecha que indique capital humano, si no que no pueda entrar, y el error sea 4 y muestre
    #un mensaje que diga que no puede entrar a la autoevaluacion por que no esta en la fecha indicada 
            
    tipo= evaluacion.numeroEvaluacion.estatus
    #Es para saber si la autoevaluacion ya fue contestada o no
    seguimiento= Seguimiento.objects.get(id=evaluacion.seguimiento_id)
    try:
        comentariosGenerales = Comentarios.objects.get(evaluacion_id=evaluacion.id)
    except:
        comentariosGenerales = []
        
    obj = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id)
    obj = Objetivos.objects.filter(numeroEvaluacion_id=evaluacion.numeroEvaluacion_id).prefetch_related('comentariosobjetivos_set', 'calificacionesobjetivos_set')
    
    cal_OKR = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=1)
    cal_KPI = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=2)
    cal_CL = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=3)
    cal_BONO = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=4)
    cal_RESULTADOS = CalificacionesObjetivos.objects.filter(evaluacion_id=evaluacion.id, objetivo__apartado_id=5)
    print ("calificaciones ", cal_OKR)
    empleadoEvaluado = evaluacion.empleado_id
    
    suma_cal_OKR = 0
    for cal in cal_OKR:
        if cal.quienCalifica_id == empleadoEvaluado:
            suma_cal_OKR = suma_cal_OKR + cal.calificacion
    
    suma_cal_KPI = 0
    for cal in cal_KPI:
        if cal.quienCalifica_id == empleadoEvaluado:
            suma_cal_KPI = suma_cal_KPI + cal.calificacion
    
    suma_cal_CL = 0
    for cal in cal_CL:
        if cal.quienCalifica_id == empleadoEvaluado and cal.estatus == 1:
            suma_cal_CL = suma_cal_CL + cal.calificacion
    
    suma_cal_BONO = 0
    for cal in cal_BONO:
        if cal.quienCalifica_id == empleadoEvaluado:
            suma_cal_BONO = suma_cal_BONO + cal.calificacion

    suma_cal_RESULTADOS = 0
    for cal in cal_RESULTADOS:
        if cal.quienCalifica_id == empleadoEvaluado :
            suma_cal_RESULTADOS = suma_cal_RESULTADOS + cal.calificacion
            
    try:
        resultados = Resultados.objects.get(evaluacion_id=evaluacion.id)
    except:
        resultados = []
    

    sumOKR = obj.filter(apartado_id=1).aggregate(total_okr=Sum('valor'))['total_okr']
    sumKPI = obj.filter(apartado_id=2).aggregate(total_kpi=Sum('valor'))['total_kpi']
    sumCL = obj.filter(apartado_id=3).values_list('valor', flat=True).first()
    

    for o in obj:
        if o.apartado_id == 3:
            objCL += o.objetivo
            metCL += o.metrica
            valCL = o.valor
            idCL = o.id

    for o in obj:
        if o.apartado_id == 4:
            siHayBono = True
        if o.apartado_id == 5:
            siHayResultados = True
            

    context ={
        "evaluacion": evaluacion,
        "obj": obj,
        "empleado": empleado,
        "sumOKR": sumOKR,
        "sumKPI": sumKPI,
        "sumCL": sumCL,
        "siHayBono": siHayBono,
        "siHayResultados": siHayResultados,
        "comentariosGenerales": comentariosGenerales,
        "seguimiento": seguimiento,
        "objCL": objCL,
        "metCL": metCL,
        "valCL": valCL,
        "idCL": idCL,
        "tipo": tipo,
        "empleado": empleado,
        "empleadoLogueado": empleadoLogueado,
        "resultados": resultados,
        "suma_cal_OKR": suma_cal_OKR,
        "suma_cal_KPI": suma_cal_KPI,
        "suma_cal_CL": suma_cal_CL,
        "suma_cal_BONO": suma_cal_BONO,
        "suma_cal_RESULTADOS": suma_cal_RESULTADOS,
        "no_emp": no_emp,
    }
    return render(request, 'reporteEvaluacionOKR.html',context)

def validarEvaluacion (request, id , tipo):
    if request.method == 'GET':
        bandera =0
        usuario=1
        print ("entra a validar evaluacion")
        print ("id ", id)
        print ("tipo ", tipo)
        evs=0
        if request.user.is_authenticated:
          usuario= request.user.id
        usuario= Usuarios.objects.get(id=usuario)      
        no_emp = usuario.no_emp
        evaluacion = None
        print ("no_emp ", no_emp)
        
        if tipo == 1:
            try:
                evaluacion = Evaluaciones.objects.get(fecha_id=id, empleado_id=no_emp)
            except Evaluaciones.DoesNotExist:
                evaluacion = None
            
        else:
            try:
                evaluacion = EvaluacionesAreas.objects.get(fecha_id=id, empleado_id=no_emp)
            except EvaluacionesAreas.DoesNotExist:
                evaluacion = None

        if evaluacion is None:
            bandera = 0
            evs = 0
        else:
            bandera = 1
            evs = evaluacion.id
            
            
            
        data = {
            'bandera': bandera
            ,'evs': evs
        }
        
    return JsonResponse(data)   