from django.contrib.auth.models import Group
from evaluaciones.models import Usuarios,Empleados,RolesUsers


#Función para obtener roles del empleado y buscar grupos relacionados a esos roles LZ 20/5/26
def user_rol(request):
    user = request.user
    data = {}

    if user.is_authenticated:
        roles = user.empleado.rol_user.all()
        group = Group.objects.filter(rolesusers__in=roles).distinct()
        group_name = list(group.values_list('name', flat=True))
        data['user_rol'] = group_name
    else:
        data['user_rol'] = []

    return data

#Función para obtener los grupos de Django del usuario LZ 20/5/26
def user_groups(request):
    if request.user.is_authenticated:
        user_groups = list(request.user.groups.values_list('name', flat=True))  
        return {
            'user_groups': user_groups,
        }
    return {}

#Función para buscar la informacion completa del usuario logueado LZ 20/5/26
def employee_info(request):
    if request.user.is_authenticated:
        try:
            data_user=Empleados.objects.get(no_emp=request.user.no_emp)
            return {'employeeInfo': data_user}
        except Empleados.DoesNotExist:
            return {'employeeInfo': None}
    return {}