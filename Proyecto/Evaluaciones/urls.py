
from django.urls import path, include
from . import views

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
    #path ('accounts/', include('django.contrib.auth.urls')),
    path('login/', views.login, name='login'),
    path ('salir/', views.salir, name='salir'),
    path('accounts/', include('django.contrib.auth.urls')),
]
