
from django.contrib import admin
from django.urls import path, include
from evaluaciones import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include ('evaluaciones.urls')),
]
