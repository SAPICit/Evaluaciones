from django import forms
from evaluaciones.models import Areas, TiposEvaluaciones, PorcentajesApartados
from django.forms import modelformset_factory


class TiposEvaluacionesForm(forms.ModelForm):

    class Meta:
        model = TiposEvaluaciones

        fields = [
            'nombre',
            'estatus',
            'descripcion',
            'dirigidoA',
        ]

        widgets = {

            'nombre': forms.TextInput(attrs={
                'class': 'form-control text-[12px]',
            }),

            'estatus': forms.Select(attrs={
                'class': 'form-control text-[12px]',
            }),

            'descripcion': forms.Textarea(attrs={
                'class': 'form-control !text-[14px]',
                'rows': 3
            }),

            'dirigidoA': forms.Select(attrs={
                'class': 'form-control text-[12px]'
            }),
        }

        labels = {
            'nombre': 'Nombre',
            'estatus': 'Estatus',
            'descripcion': 'Descripción',
            'dirigidoA': 'Dirigido a',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['nombre'] = ''
        self.initial['dirigidoA'] = 'Colaborador'

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
            'numero'
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
            'numero': forms.HiddenInput()
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['apartado'].required = False
        self.fields['tipoEvaluacion'].required = False
        self.fields['estatus'].required = False
    
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

class PorcentajesApartadosForm(forms.ModelForm):

    class Meta:
        model = PorcentajesApartados

        fields = [
            'evaluacion',
            'apartado',
            'totalApartado'
        ]

        widgets = {

            'evaluacion': forms.Select(attrs={
                'class': 'form-control text-[12px]',
            }),

            'apartado': forms.Select(attrs={
                'class': 'form-control text-[12px]',
                'placeholder': 'Nombre del apartado',
                'disabled':True
            }),

            'totalApartado': forms.NumberInput(attrs={
                'class': 'form-control text-[12px]',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'onchange':'ReloadPercentages(true)'
            }),
        }

        labels = {
            'evaluacion': 'Evaluación',
            'apartado': 'Apartado',
            'totalApartado': 'Total del apartado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['evaluacion'].empty_label = 'Selecciona una evaluación'

        self.fields['evaluacion'].required = False
        self.fields['apartado'].required = False


PorcentajesApartadosFormSet = modelformset_factory(
    PorcentajesApartados,
    form=PorcentajesApartadosForm
)
