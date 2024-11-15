from django import forms
from django.forms import ModelForm, ValidationError
from aplication.core.models import TipoMedicamento


class MedicineTypeForm(ModelForm):
  class Meta:
    model = TipoMedicamento
    fields = ["nombre", "descripcion", "activo"]

    error_messages = {
      "nombre": {
        "unique": "Ya existe este tipo de medicamento.",
      },
    }

    widgets = {
      "nombre": forms.TextInput(
        attrs={
          "placeholder": "Ingresar el tipo de medicamento",
          "id": "id_nombre",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }
      ),
      "descripcion": forms.TextInput(
        attrs={
          "placeholder": "Ingresar la descripción del tipo de medicamento",
          "id": "id_descripcion",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }
      ),
      "activo": forms.CheckboxInput(
        attrs={
          # "placeholder": "Ingresar la descripción",
          "id": "id_activo",
          "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }
      ),

    }
    labels = {
      "nombre": "Tipo Medicamento",
      "descripcion": "Descripción",
      "activo": "Tipo de Medicamento activa ?",
    }
