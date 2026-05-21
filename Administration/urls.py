from django.urls import path
from .views import *

app_name = 'Administration'

urlpatterns = [
    path('MyEvaluations/', MyEvaluationManager.as_view(), name='MyEvaluations'),
    path('EvaluationManagement/', EvaluationManagement.as_view(), name='EvaluationManagement'),
    path('ControlEvaluation/<str:action>/', ControlEvaluation.as_view(), name='ControlEvaluation'),
]