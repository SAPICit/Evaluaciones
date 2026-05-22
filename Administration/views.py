from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from .forms import AreasForm,AreasEfectividadFormSet,CalidadOperativaFormSet,CulturaLaboralFormSet, TiposEvaluacionesFormSet
from django.urls import reverse_lazy
from evaluaciones.models import Areas,TiposEvaluaciones


class MyEvaluationManager(LoginRequiredMixin, TemplateView):
    template_name = 'my_evaluations_manager.html'


class EvaluationManagement(LoginRequiredMixin, TemplateView):
    template_name = 'evaluation_management.html'

class ControlEvaluation(LoginRequiredMixin, TemplateView):
    template_name = 'creation_update_evaluation.html'

    def get(self, request, *args, **kwargs):

        context = {

            'TiposEvaluaciones_formset': TiposEvaluacionesFormSet(
                queryset=TiposEvaluaciones.objects.none(),
                prefix='TiposEvaluaciones'
            ),

            'AreasEfectividad_formset': AreasEfectividadFormSet(
                queryset=Areas.objects.none(),
                prefix='AreasEfectividad'
            ),

            'CalidadOperativa_formset': CalidadOperativaFormSet(
                queryset=Areas.objects.none(),
                prefix='CalidadOperativa'
            ),

            'CulturaLaboral_formset': CulturaLaboralFormSet(
                queryset=Areas.objects.none(),
                prefix='CulturaLaboral'
            ),
        }

        return self.render_to_response(context)