from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group




class Puestos (models.Model):
    nombre = models.TextField()
    estatus = models.SmallIntegerField()
    def __str__(self):
        return self.nombre

class Rangos (models.Model):
    nombre = models.TextField()
    estatus = models.SmallIntegerField()
    def __str__(self):
        return self.nombre
    

class Departamentos (models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.nombre
    
class Divisiones (models.Model):
    nombre = models.TextField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.nombre

class Sucursales (models.Model):
    nombre = models.TextField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.nombre
    
    
class Usuarios(AbstractUser):
    email = models.EmailField('email address', unique=True)
    no_emp = models.IntegerField('employee number', unique=True)
    rango = models.ForeignKey(Rangos,on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamentos,on_delete=models.PROTECT)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    #Funciónn para obtener el puesto del empleado
    @property
    def empleado(self):
        try:
            return Empleados.objects.get(no_emp=self.no_emp)
        except Empleados.DoesNotExist:
            return None

class RolesUsers(models.Model):
    id = models.AutoField(primary_key=True)
    name_rol      = models.CharField(verbose_name="Rol", max_length=200, null=True)
    grupos          = models.ManyToManyField(Group, blank=True)
    def __str__(self):
        return self.name_rol


class Empleados (models.Model):
    id = models.AutoField(primary_key=True)
    no_emp = models.IntegerField(unique=True)
    nombre = models.TextField()
    apellido_paterno = models.TextField()
    apellido_materno = models.TextField()
    correo = models.TextField()
    password = models.TextField()
    puesto = models.ForeignKey(Puestos,on_delete=models.PROTECT)
    rango = models.ForeignKey(Rangos,on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamentos,on_delete=models.PROTECT)
    estatus = models.SmallIntegerField()
    division = models.ForeignKey(Divisiones,on_delete=models.PROTECT)
    sucursal = models.ForeignKey(Sucursales,on_delete=models.PROTECT)
    rol_user = models.ManyToManyField(RolesUsers, related_name='Rol', blank=True)
    
    def __str__(self):
        return self.nombre + ' ' + self.apellido_paterno 
    


class Fechas(models.Model):
    id = models.AutoField(primary_key=True)
    mes = models.IntegerField()
    anio = models.IntegerField()
    version = models.IntegerField()

    def __str__(self):
        return str(self.mes) + '/' + str(self.anio) + ' V' + str(self.version)

class Apartados(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.TextField()
    valor = models.FloatField()
    estatus = models.IntegerField()

    def __str__(self):
        return self.nombre + ' ' + str(self.valor)
    
class NumerosEvaluaciones(models.Model):
    estatus = models.IntegerField()
    fechaCreacion = models.DateField()

    def __str__(self):
        return str(self.fechaCreacion)


class Objetivos(models.Model):
    objetivo = models.TextField()
    metrica = models.TextField()
    valor = models.FloatField()
    apartado = models.ForeignKey('Apartados', on_delete=models.PROTECT)
    numeroEvaluacion = models.ForeignKey('NumerosEvaluaciones', on_delete=models.PROTECT)
    estatus = models.IntegerField()

    def __str__(self):
        return self.objetivo + ' ' + self.metrica + ' ' + str(self.valor) + ' ' + str(self.apartado)  
    
class Seguimiento(models.Model):
    evaluador1 = models.ForeignKey('Empleados', to_field='no_emp',related_name='evaluador1', on_delete=models.PROTECT)
    evaluador2 = models.ForeignKey('Empleados', to_field='no_emp',related_name='evaluador2', on_delete=models.PROTECT)
    evaluador3 = models.ForeignKey('Empleados',to_field='no_emp', related_name='evaluador3', on_delete=models.PROTECT)
    evaluador4 = models.ForeignKey('Empleados',to_field='no_emp', related_name='evaluador4', on_delete=models.PROTECT)
    estatus = models.IntegerField() 
    # 1 = Todos
    # 2 = Ventas

    def __str__(self):
        return  str(self.evaluador1) +  ' ' + str(self.evaluador2) + ' '  + str(self.evaluador3) + ' ' + str(self.evaluador4) + ' ' + str(self.estatus)

class Fases (models.Model):
    nombre = models.TextField()
    estatus = models.IntegerField()

    def __str__(self):
        return self.nombre + ' ' + str(self.estatus)

class Evaluaciones (models.Model):
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    empleado = models.ForeignKey('Empleados', to_field='no_emp', on_delete=models.PROTECT)
    numeroEvaluacion = models.ForeignKey('NumerosEvaluaciones', on_delete=models.PROTECT)
    seguimiento = models.ForeignKey('Seguimiento', on_delete=models.PROTECT)
    fechaActivacion = models.DateField()
    fase = models.ForeignKey('Fases', on_delete=models.PROTECT)
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.fecha) + ' ' + str(self.empleado) + ' ' + str(self.estatus) 
    
class Resultados(models.Model):
    evaluacion = models.ForeignKey('Evaluaciones', on_delete=models.PROTECT)
    calificacion_autoevaluado = models.FloatField()
    calificacion_evaluador1 = models.FloatField()
    calificacion_evaluador2 = models.FloatField()
    calificacion_evaluador3 = models.FloatField()
    calificacion_evaluador4 = models.FloatField()
    calificacion_director = models.FloatField()
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.evaluacion) + ' ' + str(self.calificacion_autoevaluado) + ' ' + str(self.calificacion_evaluador1) + ' ' + str(self.calificacion_evaluador2) + ' ' + str(self.calificacion_evaluador3) + ' ' + str(self.calificacion_evaluador4) + ' ' + str(self.calificacion_director) + ' ' + str(self.estatus)
    
class Comentarios(models.Model):
    evaluacion = models.ForeignKey('Evaluaciones', on_delete=models.PROTECT)
    comentario_autoevaluado = models.TextField()
    comentario_evaluador1 = models.TextField()
    comentario_evaluador2 = models.TextField()
    comentario_evaluador3 = models.TextField()
    comentario_evaluador4 = models.TextField()
    comentario_director = models.TextField()
    comentario_capitalHumano = models.TextField()
    comentario_calidad = models.TextField()
    logros = models.TextField()
    estatus = models.IntegerField()

    def __str__(self):
        return  str(self.comentario_autoevaluado) + ' ' + str(self.comentario_evaluador1) + ' ' + str(self.comentario_evaluador2) + ' ' + str(self.comentario_evaluador3) + ' ' + str(self.comentario_evaluador4) + ' ' + str(self.comentario_director) + ' ' + str(self.comentario_capitalHumano) + ' ' + str(self.comentario_calidad) + ' ' + str(self.logros) + ' ' + str(self.estatus)
    
class CalificacionesObjetivos (models.Model):
    objetivo = models.ForeignKey('Objetivos', on_delete=models.PROTECT)
    evaluacion = models.ForeignKey('Evaluaciones', on_delete=models.PROTECT)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    calificacion = models.FloatField()
    quienCalifica = models.ForeignKey('Empleados', to_field='no_emp', related_name='quienCalifica',on_delete=models.PROTECT)
    fechaCalificacion = models.DateField()
    estatus = models.IntegerField()

    def __str__(self):
        return str (self.objetivo) +  ' ' + str(self.fecha) + ' ' + str(self.calificacion) + ' ' + str(self.quienCalifica) + ' ' + str(self.fechaCalificacion) + ' ' + str(self.estatus)
    
class ComentariosObjetivos (models.Model):
    objetivo = models.ForeignKey('Objetivos', on_delete=models.PROTECT)
    evaluacion = models.ForeignKey('Evaluaciones', on_delete=models.PROTECT)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    comentario = models.TextField()
    quienComenta = models.ForeignKey('Empleados', to_field='no_emp',related_name='quienComenta', on_delete=models.PROTECT)
    fechaComentario = models.DateField()
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.objetivo) + ' ' + str(self.fecha) + ' ' + str(self.comentario) + ' ' + str(self.quienComenta) + ' ' + str(self.fechaComentario) + ' ' + str(self.estatus)
    

class Calendario (models.Model):
    comentariosInicialesInicio = models.DateField()
    comentariosInicialesFin = models.DateField()
    empleadosInicio = models.DateField()
    empleadosFin = models.DateField()
    jefesInicio = models.DateField()
    jefesFin = models.DateField()
    gerentesInicio = models.DateField()
    gerentesFin = models.DateField()
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    tipo = models.IntegerField()
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.comentariosInicialesInicio) + ' ' + str(self.comentariosInicialesFin) + ' ' + str(self.empleadosInicio) + ' ' + str(self.empleadosFin) + ' '   + str(self.tipo) + ' ' + str(self.estatus)
    
    
class CalendarioFijo (models.Model):
    comentariosInicialesInicio = models.DateField()
    comentariosInicialesFin = models.DateField()
    empleadosInicio = models.DateField()
    empleadosFin = models.DateField()
    jefesInicio = models.DateField()
    jefesFin = models.DateField()
    gerentesInicio = models.DateField()
    gerentesFin = models.DateField()
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    tipo = models.IntegerField()
    status = models.IntegerField() 
    calendario = models.ForeignKey('Calendario', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.comentariosInicialesInicio) + ' ' + str(self.comentariosInicialesFin) + ' ' + str(self.empleadosInicio) + ' ' + str(self.empleadosFin) + ' '   + str(self.tipo) + ' ' + str(self.status)

#Modelo para mapear los estatus de las evaluaciones LZ 21/5/26
class EstatusEvaluaciones(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class TiposEvaluaciones(models.Model):
    estatus = models.ForeignKey(EstatusEvaluaciones,on_delete=models.PROTECT,null=True,blank=True,default=1)  
    descripcion = models.TextField()
    creador = models.ForeignKey('Empleados', to_field='no_emp',related_name='creador', on_delete=models.PROTECT,null=True,blank=True)
    fechaCreacion = models.DateTimeField(null=True,blank=True)
    departamento=models.ForeignKey(Departamentos, on_delete=models.PROTECT, null=True, blank=True, db_column='departamento_id')
    nombre = models.TextField(default='Evaluacion')
    ultimaModificacion = models.DateTimeField(null=True,blank=True)
    dirigidoA = models.CharField(max_length=50,verbose_name='Dirigido a',default='NA') 

    def __str__(self):
        return str(self.descripcion) + ' ' + str(self.estatus)

class TiposEvaluacionesHistorial(models.Model):
    estatus = models.ForeignKey(EstatusEvaluaciones,on_delete=models.PROTECT,null=True,blank=True,default=1)  
    descripcion = models.TextField()
    creador = models.ForeignKey('Empleados', to_field='no_emp',related_name='creadorHistorial', on_delete=models.PROTECT,null=True,blank=True)
    fechaCreacion = models.DateTimeField(null=True,blank=True)
    departamento=models.ForeignKey(Departamentos, on_delete=models.PROTECT, null=True, blank=True, db_column='departamento_id')
    nombre = models.TextField(default='Evaluacion')
    ultimaModificacion = models.DateTimeField(null=True,blank=True)
    dirigidoA = models.CharField(max_length=50,verbose_name='Dirigido a',default='NA') 

    def __str__(self):
        return str(self.descripcion) + ' ' + str(self.estatus)

class Areas(models.Model):
    area = models.TextField()
    metodo = models.TextField()
    objetivo = models.TextField()
    valor = models.FloatField()
    apartado = models.ForeignKey('Apartados', on_delete=models.PROTECT)
    tipoEvaluacion = models.ForeignKey('TiposEvaluaciones', on_delete=models.PROTECT)
    estatus = models.IntegerField()
    numero = models.IntegerField(default=0)

    def __str__(self):
        return self.area + ' ' + self.metodo + ' ' + str(self.valor) + ' ' + str(self.apartado)  


class AreasHistorial(models.Model):
    area = models.TextField()
    metodo = models.TextField()
    objetivo = models.TextField()
    valor = models.FloatField()
    apartado = models.ForeignKey('Apartados', on_delete=models.PROTECT)
    tipoEvaluacion = models.ForeignKey('TiposEvaluacionesHistorial', on_delete=models.PROTECT)
    estatus = models.IntegerField()
    numero = models.IntegerField(default=0)

    def __str__(self):
        return self.area + ' ' + self.metodo + ' ' + str(self.valor) + ' ' + str(self.apartado)  


class Rutas(models.Model):
    evaluador = models.ForeignKey('Empleados', to_field='no_emp',related_name='evaluador', on_delete=models.PROTECT)
    estatus = models.IntegerField() 
    # 1 = Todos
    # 2 = Ventas

    def __str__(self):
        return  str(self.evaluador) 

class Estados (models.Model):
    nombre = models.TextField()
    estatus = models.IntegerField()
    def __str__(self):
        return self.nombre + ' ' + str(self.estatus)


class EvaluacionesAreas (models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    empleado = models.ForeignKey('Empleados', to_field='no_emp', on_delete=models.PROTECT)
    tipoEvaluacion = models.ForeignKey('TiposEvaluaciones', on_delete=models.PROTECT)
    ruta = models.ForeignKey('Rutas', on_delete=models.PROTECT)
    estado = models.ForeignKey('Estados', on_delete=models.PROTECT)
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.fecha) + ' ' + str(self.empleado) + ' ' + str(self.estatus) 

#Modelo para registrar el total de los apartados por evaluacion LZ 21/5/26
class PorcentajesApartados(models.Model):
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    apartado = models.CharField(max_length=50)
    totalApartado = models.FloatField()

#Modelo para registrar el historial del total de los apartados por evaluacion LZ 21/5/26
class PorcentajesApartadosHistorial(models.Model):
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    apartado = models.CharField(max_length=50)
    totalApartado = models.FloatField()

class CalificacionesGenerales(models.Model):
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    calificacion_evaluador = models.FloatField()
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.evaluacion) + ' ' + str(self.calificacion_evaluador) 
    
class ComentariosGenerales(models.Model):
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    comentario_evaluador = models.TextField()
    comentario_director = models.TextField()
    comentario_capitalHumano = models.TextField()
    comentario_calidad = models.TextField()
    logros = models.TextField()
    estatus = models.IntegerField()

    def __str__(self):
        return   str(self.comentario_evaluador) + ' ' + str(self.comentario_director) + ' ' + str(self.comentario_capitalHumano) + ' ' + str(self.comentario_calidad) + ' ' + str(self.logros) + ' ' + str(self.estatus)


class PorcentajesAreas (models.Model):
    area = models.ForeignKey('Areas', on_delete=models.PROTECT)
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    porcentaje = models.FloatField()
    estatus = models.IntegerField()

    def __str__(self):
        return  str(self.fecha) + ' ' + str(self.estatus)
    
    
class CalificacionesAreas (models.Model):
    area = models.ForeignKey('Areas', on_delete=models.PROTECT)
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    calificacion = models.FloatField()
    fechaCalificacion = models.DateField()
    estatus = models.IntegerField()

    def __str__(self):
        return str (self.area) +  ' ' + str(self.fecha) + ' ' + str(self.calificacion) + ' '  + str(self.fechaCalificacion) + ' ' + str(self.estatus)
    
class ComentariosAreas(models.Model):
    area = models.ForeignKey('Areas', on_delete=models.PROTECT)
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    comentario = models.TextField()
    fechaComentario = models.DateField()
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.area) + ' ' + str(self.fecha) + ' ' + str(self.comentario) + ' ' + str(self.fechaComentario) + ' ' + str(self.estatus)
    
class Porcentajes(models.Model):
    area = models.ForeignKey('Areas', on_delete=models.PROTECT)
    evaluacion = models.ForeignKey('EvaluacionesAreas', on_delete=models.PROTECT)
    porcentaje = models.TextField()
    estatus = models.IntegerField()

    def __str__(self):
        return  str(self.evaluacion) + ' ' + str(self.porcentaje) + ' ' + str(self.estatus)

#    Modelo que almacena las calificaciones de los empleados por periodo de evaluación.
#    Garantiza que cada empleado tenga una única calificación por fecha.
class EvaCalificaciones(models.Model):
    no_emp = models.ForeignKey(
        'Empleados',
        to_field='no_emp',
        on_delete=models.PROTECT,
        db_column='no_emp'
    )
    fecha = models.ForeignKey(
        'Fechas',
        on_delete=models.PROTECT
    )
    calificacion = models.FloatField()
    fecha_registro = models.DateTimeField()

    class Meta:
        db_table = 'eva_calificaciones'
        unique_together = ('no_emp', 'fecha')    

# class Calendario (models.Model):
#     comentariosInicialesInicio = models.DateField()
#     comentariosInicialesFin = models.DateField()
#     empleadosInicio = models.DateField()
#     empleadosFin = models.DateField()
#     jefesInicio = models.DateField()
#     jefesFin = models.DateField()
#     gerentesInicio = models.DateField()
#     gerentesFin = models.DateField()
#     fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
#     tipo = models.IntegerField()
#     estatus = models.IntegerField()

#     def __str__(self):
#         return str(self.comentariosInicialesInicio) + ' ' + str(self.comentariosInicialesFin) + ' ' + str(self.empleadosInicio) + ' ' + str(self.empleadosFin) + ' '   + str(self.tipo) + ' ' + str(self.estatus)
    
    
# class CalendarioFijo (models.Model):
#     comentariosInicialesInicio = models.DateField()
#     comentariosInicialesFin = models.DateField()
#     empleadosInicio = models.DateField()
#     empleadosFin = models.DateField()
#     jefesInicio = models.DateField()
#     jefesFin = models.DateField()
#     gerentesInicio = models.DateField()
#     gerentesFin = models.DateField()
#     fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
#     tipo = models.IntegerField()
#     status = models.IntegerField() 
#     calendario = models.ForeignKey('Calendario', on_delete=models.PROTECT)

#     def __str__(self):
#         return str(self.comentariosInicialesInicio) + ' ' + str(self.comentariosInicialesFin) + ' ' + str(self.empleadosInicio) + ' ' + str(self.empleadosFin) + ' '   + str(self.tipo) + ' ' + str(self.status)
