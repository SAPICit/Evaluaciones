from django.shortcuts import render, redirect
from .forms import crearEmpleado, EmailAuthenticationForm
from evaluaciones.models import Empleados, Puestos, Rangos, Usuarios
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password

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
    return render(request, 'altaEmpleados.html', {'formulario': crearEmpleado(), 'puestos': puestos, 'rangos': rangos})

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

@login_required
def editarEmpleado(request, id):
    empleado = Empleados.objects.get(no_emp=id)
    puestos = Puestos.objects.all()
    rangos = Rangos.objects.all()
    return render(request, 'editarEmpleado.html', {'empleado': empleado, 'puestos': puestos, 'rangos': rangos})

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

    empleado = Empleados.objects.get(no_emp=no_emp)
    empleado.nombre = nombre
    empleado.apellido_paterno = apellido_paterno
    empleado.apellido_materno = apellido_materno
    empleado.correo = correo
    empleado.password = password
    empleado.estatus = estatus
    empleado.puesto_id = puesto_id
    empleado.rango_id = rango_id

    usuario = Usuarios.objects.get(email=correo)
    usuario.last_name = apellido_paterno
    usuario.username =  no_emp
    usuario.first_name = nombre
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

    usuario = Usuarios.objects.get(email=emp.correo)
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

    usuario = Usuarios.objects.create_user(username=no_emp, email=correo, password=password, first_name=nombre, last_name=apellido_paterno)

    empleado = Empleados(
        no_emp=no_emp,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        correo=correo,
        password=password,
        puesto_id=puesto_id,
        rango_id=rango_id,
        estatus=estatus
    )
    empleado.save()
    usuario.save()
    return redirect(reverse('listaEmpleados'))