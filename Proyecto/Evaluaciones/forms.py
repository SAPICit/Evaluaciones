from django import forms
from evaluaciones.models import Puestos, Rangos, Empleados
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

STATUS_OP=[
    ('',''),
    ('1','Activo'),
    ('0','Inactivo'),
]

class crearEmpleado(forms.Form):
    no_emp = forms.IntegerField(label='No. Empleado', required=True, widget=forms.NumberInput(attrs={'class':'form-control'}))  
    nombre = forms.CharField(label='Nombre', max_length=100, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    apellido_paterno = forms.CharField(label='Apellido Paterno', max_length=100, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    apellido_materno = forms.CharField(label='Apellido Materno', max_length=100, required=True, widget=forms.TextInput(attrs={'class':'form-control'}))
    correo = forms.EmailField(label='Correo', max_length=100, required=True, widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(label='Contraseña', max_length=100, required=True, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    estatus = forms.ChoiceField(label='Status', choices=STATUS_OP, required=True, widget=forms.Select(attrs={'class':'form-control'}))
    puesto_id = forms.ModelChoiceField(queryset=Puestos.objects.all(), label='Puesto', required=True, widget=forms.Select(attrs={'class':'form-control'}))
    rango_id = forms.ModelChoiceField(queryset=Rangos.objects.all(), label='Rango', required=True, widget=forms.Select(attrs={'class':'form-control'}))


class formularioEditarEmpleado(forms.ModelForm):
    class Meta:
        model = Empleados
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'password', 'estatus', 'puesto', 'rango']


class EmailAuthenticationForm(AuthenticationForm):
    
    email = forms.EmailField(label='Email')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data