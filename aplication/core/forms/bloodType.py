from django import forms
from django.forms import ModelForm

from aplication.core.models import TipoSangre


class BloodTypeForm(ModelForm):
  class Meta:
    model = TipoSangre
    fields = ["tipo", "descripcion"]

    error_messages = {
      "tipo": {
        "unique": "Ya existe el Tipo de Sangre.",
      },
    }

    widgets = {
      "tipo": forms.Select(
        attrs={
          "placeholder": "Example: A+",
          "id": "id_tipo",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "descripcion": forms.TextInput(
        attrs={
          "placeholder": "Example: A Positivo",
          "id": "id_descripcion",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),

    }
    labels = {
      "tipo": "Tipo de Sangre",
      "descripcion": "Descripción del Tipo de Sangre",
    }
