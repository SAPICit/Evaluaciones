from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Puestos, Rangos, Empleados, Apartados, Objetivos, Fechas, Calificaciones, Seguimientos,Evaluaciones, ObjetivosMensuales,ComentariosIndividuales

# Register your models here.

# class RecursosHumanosPuestos(admin.ModelAdmin):
#     list_display = ['id', 'nombre', 'Departamento', 'estatus']

# class RecursosHumanosRangos(admin.ModelAdmin):
#     list_display = ['id', 'nombre', 'estatus']

# class RecursosHumanosEmpleados(admin.ModelAdmin):
#     list_display = ['id', 'no_emp', 'nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'puesto', 'rango', 'jefe_inmeditao','estatus']


# Registra los modelos con el ModelAdmin personalizado
# admin.site.register(Puestos, RecursosHumanosPuestos)
# admin.site.register(Rangos, RecursosHumanosRangos)
# admin.site.register(Empleados, RecursosHumanosEmpleados) 

admin.site.register(Puestos)
admin.site.register(Rangos)
admin.site.register(Empleados) 
admin.site.register(Apartados) 
admin.site.register(Objetivos) 
admin.site.register(Fechas)    
admin.site.register(Calificaciones)
admin.site.register(Seguimientos)  
admin.site.register(Evaluaciones)
admin.site.register(ObjetivosMensuales)
admin.site.register(ComentariosIndividuales)


# Crea un grupo de recursos humanos y asigna los permisos necesarios
group, created = Group.objects.get_or_create(name='Recursos Humanos')

# Obtiene los permisos para los modelos específicos
content_type = ContentType.objects.get_for_models(Puestos, Rangos, Empleados)
permissions = Permission.objects.filter(content_type__in=content_type.values())

# Asigna los permisos al grupo de recursos humanos
group.permissions.set(permissions)
    