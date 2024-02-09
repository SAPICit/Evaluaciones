from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Puestos, Rangos, Empleados, Apartados, Objetivos, Fechas, Calificaciones, Seguimientos,Evaluaciones, ObjetivosMensuales,ComentariosIndividuales, Usuarios

admin.site.register(Usuarios)
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


    
