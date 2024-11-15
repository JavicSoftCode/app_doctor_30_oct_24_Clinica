from django import forms
from django.forms import ModelForm

from aplication.core.models import CategoriaExamen


class CategoryExamenForm(ModelForm):
  class Meta:
    model = CategoriaExamen
    fields = ["nombre", "descripcion", "activo"]

    error_messages = {
      "nombre": {
        "unique": "Ya existe la Categoría Examen.",
      },
    }

    widgets = {
      "nombre": forms.TextInput(
        attrs={
          "placeholder": "Ingresar categoría examen",
          "id": "id_nombre",
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
      "activo": forms.CheckboxInput(
        attrs={
          "id": "id_activo",
          "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),

    }
    labels = {
      "nombre": "Categoría Examen",
      "descripcion": "Descripción",
      "activo": "Categoría de Examen activa ?",
    }
