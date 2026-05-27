from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from .forms import AreasForm,AreasEfectividadFormSet,CalidadOperativaFormSet,CulturaLaboralFormSet, TiposEvaluacionesFormSet, PorcentajesApartadosFormSet
from django.urls import reverse_lazy
from evaluaciones.models import Areas,TiposEvaluaciones,PorcentajesApartados, Apartados
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect


class MyEvaluationManager(LoginRequiredMixin, TemplateView):
    template_name = 'my_evaluations_manager.html'


class EvaluationManagement(LoginRequiredMixin, TemplateView):
    template_name = 'evaluation_management.html'

class ControlEvaluation(LoginRequiredMixin, TemplateView):
    template_name = 'creation_update_evaluation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['TiposEvaluaciones_formset'] = TiposEvaluacionesFormSet(
            queryset=TiposEvaluaciones.objects.none(),
            prefix='TiposEvaluaciones'
        )

        context['AreasEfectividad_formset'] = AreasEfectividadFormSet(
            queryset=Areas.objects.none(),
            prefix='AreasEfectividad',
        )

        context['CalidadOperativa_formset'] = CalidadOperativaFormSet(
            queryset=Areas.objects.none(),
            prefix='CalidadOperativa'
        )

        context['CulturaLaboral_formset'] = CulturaLaboralFormSet(
            queryset=Areas.objects.none(),
            prefix='CulturaLaboral'
        )

        context['AreasEfectividadPorcentaje_formset'] = PorcentajesApartadosFormSet(
            queryset=PorcentajesApartados.objects.none(),
            prefix='AreasEfectividadPorcentaje',
                initial=[
                    {
                        'apartado': 'AreasEfectividad',
                        'totalApartado': 80
                    }]
        )

        context['CalidadOperativaPorcentaje_formset'] = PorcentajesApartadosFormSet(
            queryset=PorcentajesApartados.objects.none(),
            prefix='CalidadOperativaPorcentaje',
                initial=[
                    {
                        'apartado': 'CalidadOperativa',
                        'totalApartado': 10
                    }]
        )

        context['CulturaLaboralPorcentaje_formset'] = PorcentajesApartadosFormSet(
            queryset=PorcentajesApartados.objects.none(),
            prefix='CulturaLaboralPorcentaje',
                initial=[
                    {
                        'apartado': 'CulturaLaboral',
                        'totalApartado': 10
                    }]
        )

        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        TiposEvaluaciones_fs = TiposEvaluacionesFormSet(
            request.POST,
            prefix='TiposEvaluaciones'
        )

        AreasEfectividad_fs = AreasEfectividadFormSet(
            request.POST,
            prefix='AreasEfectividad'
        )

        CalidadOperativa_fs = CalidadOperativaFormSet(
            request.POST,
            prefix='CalidadOperativa'
        )

        CulturaLaboral_fs = CulturaLaboralFormSet(
            request.POST,
            prefix='CulturaLaboral'
        )

        AreasEfectividadPorcentaje_fs = PorcentajesApartadosFormSet(
            request.POST,
            prefix='AreasEfectividadPorcentaje'
        )

        CalidadOperativaPorcentaje_fs = PorcentajesApartadosFormSet(
            request.POST,
            prefix='CalidadOperativaPorcentaje'
        )

        CulturaLaboralPorcentaje_fs = PorcentajesApartadosFormSet(
            request.POST,
            prefix='CulturaLaboralPorcentaje'
        )


        if not TiposEvaluaciones_fs.is_valid():
            print('TiposEvaluaciones errors:')
            print(TiposEvaluaciones_fs.errors)
            print(TiposEvaluaciones_fs.non_form_errors())

        if not AreasEfectividad_fs.is_valid():
            print('AreasEfectividad errors:')
            print(AreasEfectividad_fs.errors)
            print(AreasEfectividad_fs.non_form_errors())

        if not CalidadOperativa_fs.is_valid():
            print('CalidadOperativa errors:')
            print(CalidadOperativa_fs.errors)
            print(CalidadOperativa_fs.non_form_errors())

        if not CulturaLaboral_fs.is_valid():
            print('CulturaLaboral errors:')
            print(CulturaLaboral_fs.errors)
            print(CulturaLaboral_fs.non_form_errors())

        if not AreasEfectividadPorcentaje_fs.is_valid():
            print('AreasEfectividadPorcentaje_fs errors:')
            print(AreasEfectividadPorcentaje_fs.errors)
            print(AreasEfectividadPorcentaje_fs.non_form_errors())

        if not CalidadOperativaPorcentaje_fs.is_valid():
            print('CalidadOperativaPorcentaje_fs errors:')
            print(CalidadOperativaPorcentaje_fs.errors)
            print(CalidadOperativaPorcentaje_fs.non_form_errors())

        if not CulturaLaboralPorcentaje_fs.is_valid():
            print('CulturaLaboralPorcentaje_fs errors:')
            print(CulturaLaboralPorcentaje_fs.errors)
            print(CulturaLaboralPorcentaje_fs.non_form_errors())
        

        formsets_validos = all([
            TiposEvaluaciones_fs.is_valid(),
            AreasEfectividad_fs.is_valid(),
            CalidadOperativa_fs.is_valid(),
            CulturaLaboral_fs.is_valid(),
            AreasEfectividadPorcentaje_fs.is_valid(),
            CalidadOperativaPorcentaje_fs.is_valid(),
            CulturaLaboralPorcentaje_fs.is_valid(),
        ])

        if formsets_validos:

            # ==========================================
            # GUARDAR TIPO EVALUACION
            # ==========================================

            tipo_evaluacion = TiposEvaluaciones_fs.save(commit=False)[0]

            tipo_evaluacion.creador = request.user.empleado
            tipo_evaluacion.fechaCreacion = timezone.now()
            tipo_evaluacion.ultimaModificacion = timezone.now()

            tipo_evaluacion.save()

            # ==========================================
            # FUNCION PARA GUARDAR AREAS
            # ==========================================

            def guardar_areas(formset, name_section):
                apartado = Apartados.objects.filter(nombre=name_section).first()

                for index, form in enumerate(formset.forms):

                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):

                        area = form.save(commit=False)

                        area.tipoEvaluacion = tipo_evaluacion
                        area.estatus = 1
                        area.apartado = apartado
                        area.save()

            guardar_areas(AreasEfectividad_fs, 'Areas Efectividad')
            guardar_areas(CalidadOperativa_fs,'Calidad Operativa')
            guardar_areas(CulturaLaboral_fs,'Cultura Laboral')

            # ==========================================
            # GUARDAR PORCENTAJES
            # ==========================================

            def guardar_porcentajes(formset):

                for form in formset.forms:

                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):

                        porcentaje = form.save(commit=False)

                        porcentaje.evaluacion = tipo_evaluacion

                        porcentaje.save()

            guardar_porcentajes(AreasEfectividadPorcentaje_fs)
            guardar_porcentajes(CalidadOperativaPorcentaje_fs)
            guardar_porcentajes(CulturaLaboralPorcentaje_fs)

            messages.success(request, 'Evaluación creada correctamente')

            return redirect('Administration:MyEvaluations')

        # ==========================================
        # SI HAY ERRORES
        # ==========================================

        context = {
            'TiposEvaluaciones_formset': TiposEvaluaciones_fs,
            'AreasEfectividad_formset': AreasEfectividad_fs,
            'CalidadOperativa_formset': CalidadOperativa_fs,
            'CulturaLaboral_formset': CulturaLaboral_fs,
            'AreasEfectividadPorcentaje_formset': AreasEfectividadPorcentaje_fs,
            'CalidadOperativaPorcentaje_formset': CalidadOperativaPorcentaje_fs,
            'CulturaLaboralPorcentaje_formset': CulturaLaboralPorcentaje_fs,
        }

        messages.error(request, 'Hay errores en el formulario')

        return self.render_to_response(context)