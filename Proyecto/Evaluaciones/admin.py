from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Puestos, Rangos, Empleados, Usuarios, Departamentos, Fechas, Apartados, Evaluaciones, ComentariosObjetivos, CalificacionesObjetivos, Resultados, Comentarios, Seguimiento, Objetivos, NumerosEvaluaciones, Fases

admin.site.register(Usuarios)
admin.site.register(Puestos)
admin.site.register(Rangos)
admin.site.register(Empleados)
admin.site.register(Departamentos)
admin.site.register(Fechas)
admin.site.register(Apartados)
admin.site.register(Evaluaciones)
admin.site.register(ComentariosObjetivos)
admin.site.register(CalificacionesObjetivos)
admin.site.register(Resultados)
admin.site.register(Comentarios)
admin.site.register(Seguimiento)
admin.site.register(Objetivos)
admin.site.register(NumerosEvaluaciones)
admin.site.register(Fases)

    
