from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
import datetime
from aplication.attention.models import CitaMedica


class CitaMedicaForm(ModelForm):
  class Meta:
    model = CitaMedica
    fields = [
      "paciente",
      "fecha",
      "hora_cita",
      "estado"
    ]

    error_messages = {
      "paciente": {
        "required": "Seleccionar al paciente.",
      },
      "fecha": {
        "required": "Ingresar fecha de la cita médica.",
      },
      "hora_cita": {
        "required": "Ingresar hora de la cita médica.",
      },
      "estado": {
        "required": "Seleccionar el estado de la cita médica.",
      },
    }

    widgets = {
      "paciente": forms.Select(attrs={
        "id": "id_paciente",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"},
      ),
      "fecha": forms.DateInput(attrs={
        "type": "date",
        "id": "id_fecha",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"},
        format='%Y-%m-%d'
      ),
      "hora_cita": forms.TimeInput(attrs={
        "placeholder": "Seleccionar la hora de la cita",
        "id": "id_hora_cita",
        "type": "time",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"},
      ),
      "estado": forms.Select(attrs={
        "id": "id_estado",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"},
      ),

    }
    labels = {
      "paciente": "Paciente",
      "fecha": "Fecha",
      "hora_cita": "Hora",
      "estado": "Cita Médica",
    }
