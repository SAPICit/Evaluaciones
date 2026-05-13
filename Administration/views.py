from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class MyEvaluationManager(LoginRequiredMixin, TemplateView):
    template_name = 'my_evaluations_manager.html'


class EvaluationManagement(LoginRequiredMixin, TemplateView):
    template_name = 'evaluation_management.html'