from django.db import models
from django.utils import timezone


class Puestos (models.Model):
    nombre = models.TextField()
    departamento = models.TextField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.nombre + ' - ' + self.departamento

class Rangos (models.Model):
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
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.nombre + ' ' + self.apellido_paterno + ' ' + self.apellido_materno
    
class Apartados (models.Model):
    nombre = models.TextField()
    valor = models.FloatField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.nombre
    
class Objetivos (models.Model):
    objetivo= models.TextField()
    metrica = models.TextField()
    valor = models.FloatField()
    apartado = models.ForeignKey(Apartados,on_delete=models.PROTECT)
    estatus = models.SmallIntegerField()

    def __str__(self):
        return self.objetivo + ' - ' + self.metrica
    
class Fechas (models.Model):
    mes = models.SmallIntegerField()
    anio = models.SmallIntegerField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return f"{self.mes} - {self.anio}"
    
class Calificaciones (models.Model):
    empleado = models.ForeignKey(Empleados, to_field='no_emp',on_delete=models.PROTECT)
    fecha = models.ForeignKey(Fechas,on_delete=models.PROTECT)
    cal_autoevaluacion = models.FloatField()
    cal_jefe = models.FloatField()
    cal_administrador = models.FloatField()
    cal_supervisor = models.FloatField()
    cal_director = models.FloatField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return str(self.calificacion) + ' - ' + str(self.empleado) 
    
class Seguimientos (models.Model):
    empleado = models.ForeignKey(Empleados, to_field='no_emp', on_delete=models.PROTECT, related_name='seguimientos_empleado')
    fecha = models.ForeignKey(Fechas, on_delete=models.PROTECT)
    id_evaluador1 = models.ForeignKey(Empleados, to_field='no_emp', on_delete=models.PROTECT, related_name='seguimientos_evaluador1')
    contestado_evaludado1 = models.BooleanField()
    id_evaluador2 = models.ForeignKey(Empleados, to_field='no_emp', on_delete=models.PROTECT, related_name='seguimientos_evaluador2')
    contestado_evaludado2 = models.BooleanField()
    id_evaluador3 = models.ForeignKey(Empleados, to_field='no_emp', on_delete=models.PROTECT, related_name='seguimientos_evaluador3')
    contestado_evaludado3 = models.BooleanField()
    id_evaluador4 = models.ForeignKey(Empleados, to_field='no_emp', on_delete=models.PROTECT, related_name='seguimientos_evaluador4')
    contestado_evaludado4 = models.BooleanField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return str(self.empleado) + ' - ' + str(self.fecha)
    
class Evaluaciones (models.Model):
    empleado = models.ForeignKey(Empleados, to_field='no_emp',on_delete=models.PROTECT)
    seguimiento = models.ForeignKey(Seguimientos,on_delete=models.PROTECT)
    fecha = models.ForeignKey(Fechas,on_delete=models.PROTECT)
    comentarios_autoevaluado = models.TextField()
    comentarios_jefe = models.TextField()
    comentarios_director = models.TextField()
    comentarios_supervisor = models.TextField()
    comentarios_administrador = models.TextField()
    calificacion = models.ForeignKey(Calificaciones,on_delete=models.PROTECT)
    estatus = models.SmallIntegerField()
    fechaActivacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.seguimiento) + ' - ' + str(self.objetivo)
    
class ObjetivosMensuales (models.Model):
    empleado = models.ForeignKey(Empleados, to_field='no_emp',on_delete=models.PROTECT)
    fecha = models.ForeignKey(Fechas,on_delete=models.PROTECT)
    objetivo = models.ForeignKey(Objetivos,on_delete=models.PROTECT)
    evaluacion = models.ForeignKey(Evaluaciones,on_delete=models.PROTECT)
    cal_autoevaluacion = models.FloatField()
    cal_jefe = models.FloatField()
    cal_director = models.FloatField()
    cal_administrador = models.FloatField()
    cal_supervisor = models.FloatField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return str(self.evaluacion) + ' - ' + str(self.objetivo) + ' - ' + str(self.fecha) + ' - ' + str(self.empleado)

class ComentariosIndividuales (models.Model):
    ObjetivoMensual = models.ForeignKey(ObjetivosMensuales,on_delete=models.PROTECT)
    empleadoComentario = models.ForeignKey(Empleados, to_field='no_emp',on_delete=models.PROTECT)
    fecha = models.ForeignKey(Fechas,on_delete=models.PROTECT)
    comentario = models.TextField()
    estatus = models.SmallIntegerField()

    def __str__(self):
        return  str(self.fecha) + ' - ' + str(self.empleadoComentario) + ' - ' + str(self.comentario)



