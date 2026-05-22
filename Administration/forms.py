from django import forms
from evaluaciones.models import Areas, TiposEvaluaciones
from django.forms import modelformset_factory


class TiposEvaluacionesForm(forms.ModelForm):

    class Meta:
        model = TiposEvaluaciones
        fields = ['estatus', 'descripcion']

        widgets = {
            'estatus': forms.NumberInput(attrs={
                'class': 'form-control text-[12px]',
                'placeholder': 'Estatus'
            }),

            'descripcion': forms.Textarea(attrs={
                'class': 'form-control !text-[14px]',
                'rows': 3
            }),
        }

        labels = {
            'estatus': 'Estatus',
            'descripcion': 'Descripción',
        }

TiposEvaluacionesFormSet = modelformset_factory(
    TiposEvaluaciones,
    form=TiposEvaluacionesForm,
    extra=1
)

class AreasForm(forms.ModelForm):
    class Meta:
        model = Areas
        fields = [
            'area',
            'metodo',
            'objetivo',
            'valor',
            'apartado',
            'tipoEvaluacion',
            'estatus',
        ]

        widgets = {
            'area': forms.Textarea(attrs={
                'class': 'form-control !text-[14px]',
                'rows': 3,
            }),
            'metodo': forms.Textarea(attrs={
                'class': 'form-control !text-[14px]',
                'rows': 3,
            }),
            'objetivo': forms.Textarea(attrs={
                'class': 'form-control !text-[14px]',
                'rows': 3,
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control !text-[14px]',
                'step': '0.01',
            }),
            'apartado': forms.Select(attrs={
                'class': 'form-select',
            }),
            'tipoEvaluacion': forms.Select(attrs={
                'class': 'form-select',
            }),
            'estatus': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }

        labels = {
            'area': 'Área',
            'metodo': 'Método',
            'objetivo': 'Objetivo',
            'valor': 'Valor',
            'apartado': 'Apartado',
            'tipoEvaluacion': 'Tipo de evaluación',
            'estatus': 'Estatus',
        }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')

        if valor < 0:
            raise forms.ValidationError('El valor no puede ser negativo.')

        return valor
    
AreasEfectividadFormSet = modelformset_factory(
    Areas,
    form=AreasForm,
    extra=1,
    can_delete=True
)

CalidadOperativaFormSet = modelformset_factory(
    Areas,
    form=AreasForm,
    extra=1,
    can_delete=True
)

CulturaLaboralFormSet = modelformset_factory(
    Areas,
    form=AreasForm,
    extra=1,
    can_delete=True
)


