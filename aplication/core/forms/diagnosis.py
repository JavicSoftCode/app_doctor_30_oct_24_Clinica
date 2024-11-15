from django import forms
from django.forms import ModelForm

from aplication.core.models import Diagnostico


class DiagnosisForm(ModelForm):
  class Meta:
    model = Diagnostico
    fields = ["codigo", "descripcion", "datos_adicionales", "activo"]

    error_messages = {
      "codigo": {
        "unique": "Ya existe la Especialidad.",
      },
    }

    widgets = {
      "codigo": forms.TextInput(
        attrs={
          "readonly": True,
          "placeholder": "Ingresar codigo",
          "id": "id_codigo",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "descripcion": forms.TextInput(
        attrs={
          "placeholder": "Ingresar la descripción",
          "id": "id_descripcion",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "datos_adicionales": forms.TextInput(
        attrs={
          "placeholder": "Ingresar datos adicionales",
          "id": "id_datos_adicionales",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "activo": forms.CheckboxInput(
        attrs={
          "id": "id_activo",
          "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),

    }
    labels = {
      "codigo": "Código del Diagnostico",
      "descripcion": "Descripción",
      "datos_adicionales": "Datos Adicionales",
      "activo": "Diagnostico activo ?",
    }
