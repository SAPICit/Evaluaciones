# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApartadosAntiguos(models.Model):
    id_apartado = models.AutoField(primary_key=True)
    no_apartado = models.IntegerField()
    no_emp = models.IntegerField()
    valor_apartado = models.FloatField()
    nom_apartado = models.CharField(max_length=500)
    proyectos = models.IntegerField()
    version = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'apartados'


class ApartadosMes(models.Model):
    id_apartadomes = models.AutoField(db_column='id_apartadoMes', primary_key=True)  # Field name made lowercase.
    id_apartado = models.IntegerField()
    mes = models.CharField(max_length=50)
    año = models.IntegerField()
    no_emp = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'apartados_mes'


class CalifApartado(models.Model):
    id_apartado = models.AutoField(primary_key=True)
    no_emp = models.IntegerField()
    mes = models.CharField(max_length=25)
    año = models.IntegerField()
    apartado = models.IntegerField()
    calif = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'calif_apartado'


class Empleado(models.Model):
    no_emp = models.IntegerField()
    nom_emp = models.CharField(max_length=100)
    evalua_ger = models.IntegerField(db_comment='0 no, 1 si')
    puesto_emp = models.CharField(max_length=100)
    jefe_inmediato = models.CharField(max_length=100)
    rango = models.CharField(max_length=30)
    departamento = models.CharField(max_length=10)
    codigo = models.CharField(max_length=10)
    correo = models.CharField(max_length=200)
    password = models.CharField(max_length=100)
    version = models.IntegerField()
    empactivo = models.IntegerField(db_comment='0 si, 1 no')
    validamenu = models.IntegerField(db_comment='0-EMP,1-EMP y QUEJ,2:TODO')

    class Meta:
        managed = False
        db_table = 'empleado'


class EvaluacionesAntiguos(models.Model):
    id_evaluaciones = models.AutoField(primary_key=True)
    no_emp = models.IntegerField()
    mes_evaluacion = models.CharField(max_length=50)
    puntuacion_auto = models.FloatField()
    puntuacion_total = models.FloatField(db_comment='calif jefe')
    puntuacion_adm = models.FloatField()
    puntuacion_gerente = models.FloatField()
    puntuacion_director = models.FloatField()
    comen_compromisos = models.CharField(max_length=500)
    logro = models.TextField()
    comen_compromisos_jefe = models.CharField(max_length=500)
    comen_compromisos_jefe_jefe = models.CharField(max_length=500, db_comment='adm')
    comen_compromisos_ger = models.CharField(max_length=9999)
    comen_compromisos_dir = models.TextField()
    comen_compromisos_adm = models.CharField(max_length=9999)
    anio_evaluacion = models.IntegerField()
    fase = models.IntegerField()
    poseedor = models.IntegerField()
    estatus = models.CharField(max_length=7)
    fecha_evalua = models.DateField()
    guardado = models.IntegerField(db_comment='1-si, 0-no')

    class Meta:
        managed = False
        db_table = 'evaluaciones'


class Evaluaobjetivos(models.Model):
    id_evaluaobj = models.AutoField(primary_key=True)
    id_obj = models.IntegerField()
    evalua_auto = models.CharField(max_length=2)
    evalua_jefe = models.CharField(max_length=2)
    evalua_jefe_jefe = models.CharField(max_length=3, db_comment='adm')
    evalua_gerente = models.CharField(max_length=2)
    valorcalif_auto = models.FloatField()
    valorcalif_jefe = models.FloatField()
    valorcalif_jefe_jefe = models.FloatField()
    comentarios_emp = models.CharField(max_length=300)
    comentarios_jefe = models.CharField(max_length=1000)
    comentarios_queja = models.CharField(max_length=500)
    mesevalua = models.CharField(max_length=500)
    anioevalua = models.IntegerField()
    no_empleado = models.IntegerField()
    valorcalif_gerente = models.FloatField()
    comentarios_jefe_jefe = models.CharField(max_length=1000)
    comentarios_gerente = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'evaluaobjetivos'


class ObjetivosAntiguos(models.Model):
    id_obj = models.AutoField(primary_key=True)
    objetivo = models.TextField(db_collation='utf8_general_ci')
    metrica1 = models.TextField()
    metrica2 = models.CharField(max_length=150)
    metrica3 = models.CharField(max_length=500)
    valor = models.FloatField()
    id_apartado = models.IntegerField()
    mesevalua = models.CharField(max_length=10)
    anio = models.IntegerField()
    version = models.IntegerField()
    borrado = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'objetivos'


class Preevaluaobjetivos(models.Model):
    id_evaluaobj = models.AutoField(primary_key=True)
    id_obj = models.IntegerField()
    evalua_adm = models.CharField(max_length=2)
    calif_adm = models.FloatField()
    mesevalua = models.CharField(max_length=10)
    anioevalua = models.IntegerField()
    no_empleado = models.IntegerField()
    comentarios_adm = models.CharField(max_length=9999)

    class Meta:
        managed = False
        db_table = 'preevaluaobjetivos'


class Quejas(models.Model):
    id_queja = models.AutoField(primary_key=True)
    no_emp = models.IntegerField()
    descripcion_queja = models.CharField(max_length=500)
    id_apartado = models.IntegerField()
    id_objetivo = models.IntegerField()
    mesevalua = models.CharField(max_length=10)
    anioevalua = models.IntegerField()
    quien_queja = models.IntegerField()
    fecha_queja = models.DateField()

    class Meta:
        managed = False
        db_table = 'quejas'


class RutaEvalua(models.Model):
    id_ruta = models.AutoField(primary_key=True)
    no_emp = models.IntegerField()
    segundo = models.IntegerField()
    ok2 = models.CharField(max_length=2)
    tercero = models.IntegerField()
    ok3 = models.CharField(max_length=2)
    cuarto = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ruta_evalua'


class Table9(models.Model):
    col_1 = models.CharField(db_column='COL 1', max_length=11, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    col_2 = models.CharField(db_column='COL 2', max_length=11, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    col_3 = models.CharField(db_column='COL 3', max_length=6, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    col_4 = models.CharField(db_column='COL 4', max_length=14, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    col_5 = models.CharField(db_column='COL 5', max_length=30, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    col_6 = models.CharField(db_column='COL 6', max_length=9, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    col_7 = models.CharField(db_column='COL 7', max_length=7, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'table 9'


class Versiones(models.Model):
    id_version = models.AutoField(primary_key=True)
    no_emp = models.IntegerField()
    mes = models.CharField(max_length=11)
    año = models.IntegerField()
    version = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'versiones'
