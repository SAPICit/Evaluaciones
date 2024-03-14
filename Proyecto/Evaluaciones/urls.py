
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    #path('', LoginView.as_view(template_name='index.html'), name='login'),
    path('index/', views.index),
    path('imagenes/', views.imagenes),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('altaEmpleados/', views.altaEmpleados, name='altaEmpleados'),
    path('guardarEmpleado/', views.guardarEmpleado, name='guardarEmpleado'),
    path('listaEmpleados/', views.listaEmpleados, name='listaEmpleados'),
    path('editarEmpleado/<int:id>/', views.editarEmpleado, name='editarEmpleado'),
    path('eliminarEmpleado/<int:id>/', views.eliminarEmpleado, name='eliminarEmpleado'),
    path('guardar', views.guardar, name='guardar'),
    path('login/', views.login, name='login'),
    path ('salir/', views.salir, name='salir'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('evaluaciones/', views.evaluaciones, name='evaluaciones'),
    path('crearEvaluacion/', views.crearEvaluacion, name='crearEvaluacion'),
    path('crearEvaluacion2/', views.crearEvaluacion2, name='crearEvaluacion2'),
    path('crearEvaluacionDB/<str:arregloBonos>/<str:arregloCLs>/<str:arregloKPIs>/<str:arregloOKRs>/', views.crearEvaluacionDB, name='crearEvaluacionDB'),
    path('guardarEvaluacionBD/', views.guardarEvaluacionBD, name='guardarEvaluacionBD'),
    path ('asignarEvaluacion/', views.asignarEvaluacion, name='asignarEvaluacion'),
    path ('obtener_datos_evaluacion/', views.obtener_datos_evaluacion, name='obtener_datos_evaluacion'),
    path ('rutaEvaluacion/', views.rutaEvaluacion, name='rutaEvaluacion'),
    path ('guardarRutaEvaluacion/', views.guardarRutaEvaluacion, name='guardarRutaEvaluacion'),
    path ('obtener_datos_seguimiento/', views.obtener_datos_seguimiento, name='obtener_datos_seguimiento'),
    path ('guardarEvaluacionMensual', views.guardarEvaluacionMensual, name='guardarEvaluacionMensual'),
    path ('guardarEvaluacionEditada', views.guardarEvaluacionEditada, name='guardarEvaluacionEditada'),
    path ('editarEvaluacion/', views.editarEvaluacion, name='editarEvaluacion'),
    path ('obtener_datos_evaluaciones/', views.obtener_datos_evaluaciones, name='obtener_datos_evaluaciones'),
    path ('obtener_datos_evaluaciones_editada/', views.obtener_datos_evaluaciones_editada, name='obtener_datos_evaluaciones_editada'),
    path ('editarEvaluacionAsignada/<int:id>/', views.editarEvaluacionAsignada, name='editarEvaluacionAsignada'),
    path ('comentariosInicio/', views.comentariosInicio, name='comentariosInicio'),
    path ('guardar_comentarios_iniciales/', views.guardar_comentarios_iniciales, name='guardar_comentarios_iniciales'),
    path ('autoevaluacion/', views.autoevaluacion, name='autoevaluacion'),
    path ('obtener_datos_evaluacion_comentarios/', views.obtener_datos_evaluacion_comentarios, name='obtener_datos_evaluacion_comentarios'),
    path ('calendario/', views.calendario, name='calendario'),
    path ('traerDatosEmpleado/', views.traerDatosEmpleado, name='traerDatosEmpleado'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
