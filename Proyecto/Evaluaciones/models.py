from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Usuarios(AbstractUser):
    email = models.EmailField('email address', unique=True)
    no_emp = models.IntegerField('employee number', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


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
    nombre = models.TextField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.nombre

class Empleados (models.Model):
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

    def __str__(self):
        return self.nombre + ' ' + self.apellido_paterno 
    

class Fechas(models.Model):
    mes = models.IntegerField()
    anio = models.IntegerField()
    version = models.IntegerField()

    def __str__(self):
        return str(self.mes) + '/' + str(self.anio) + ' V' + str(self.version)

class Apartados(models.Model):
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
        return self.objetivo + ' ' + self.metrica + ' ' + str(self.valor) + ' ' + str(self.apartado) + ' ' + str(self.tipoEvaluacion)
    
class Seguimiento(models.Model):
    evaluador1 = models.ForeignKey('Empleados', to_field='no_emp',related_name='evaluador1', on_delete=models.PROTECT)
    evaluador2 = models.ForeignKey('Empleados', to_field='no_emp',related_name='evaluador2', on_delete=models.PROTECT)
    evaluador3 = models.ForeignKey('Empleados',to_field='no_emp', related_name='evaluador3', on_delete=models.PROTECT)
    evaluador4 = models.ForeignKey('Empleados',to_field='no_emp', related_name='evaluador4', on_delete=models.PROTECT)
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.no_emp) + ' ' + str(self.fecha) + ' ' + str(self.evaluador1) +  ' ' + str(self.evaluador2) + ' '  + str(self.evaluador3) + ' ' + str(self.evaluador4) + ' ' + str(self.estatus)

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

    def __str__(self):
        return str(self.resultado) + ' ' + str(self.comentario_autoevaluado) + ' ' + str(self.comentario_evaluador1) + ' ' + str(self.comentario_evaluador2) + ' ' + str(self.comentario_evaluador3) + ' ' + str(self.comentario_evaluador4) + ' ' + str(self.comentario_director)
    
class CalificacionesObjetivos (models.Model):
    objetivo = models.ForeignKey('Objetivos', on_delete=models.PROTECT)
    empleado = models.ForeignKey('Empleados', to_field='no_emp', related_name='empleadoCalificado',on_delete=models.PROTECT)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    calificacion = models.FloatField()
    quienCalifica = models.ForeignKey('Empleados', to_field='no_emp', related_name='quienCalifica',on_delete=models.PROTECT)
    fechaCalificacion = models.DateField()
    estatus = models.IntegerField()

    def __str__(self):
        return str (self.objetivo) + ' ' + str(self.empleado) + ' ' + str(self.fecha) + ' ' + str(self.calificacion) + ' ' + str(self.quienCalifica) + ' ' + str(self.fechaCalificacion) + ' ' + str(self.estatus)
    
class ComentariosObjetivos (models.Model):
    objetivo = models.ForeignKey('Objetivos', on_delete=models.PROTECT)
    empleado = models.ForeignKey('Empleados', to_field='no_emp', related_name='empleadoComentado',on_delete=models.PROTECT)
    fecha = models.ForeignKey('Fechas', on_delete=models.PROTECT)
    comentario = models.TextField()
    quienComenta = models.ForeignKey('Empleados', to_field='no_emp',related_name='quienComenta', on_delete=models.PROTECT)
    fechaComentario = models.DateField()
    estatus = models.IntegerField()

    def __str__(self):
        return str(self.objetivo) + ' ' + str(self.empleado) + ' ' + str(self.fecha) + ' ' + str(self.comentario) + ' ' + str(self.quienComenta) + ' ' + str(self.fechaComentario) + ' ' + str(self.estatus)