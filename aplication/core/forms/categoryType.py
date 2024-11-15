# forms.py
from django import forms
from django.forms import ModelForm

from aplication.core.models import TipoCategoria


class CategoryTypeForm(ModelForm):
  class Meta:
    model = TipoCategoria
    fields = ["categoria_examen", "nombre", "descripcion", "valor_minimo", "valor_maximo", "activo"]

    error_messages = {
      "nombre": {
        "unique": "Ya existe un examen con este nombre.",
      },
    }

    widgets = {
      "categoria_examen": forms.Select(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "nombre": forms.TextInput(
        attrs={
          "placeholder": "Ingresar nombre del examen",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "descripcion": forms.Textarea(
        attrs={
          "placeholder": "Ingresar descripción del examen",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
          "rows": 2,
        },
      ),
      "valor_minimo": forms.TextInput(
        attrs={
          "placeholder": "Ingresar valor mínimo de referencia",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "valor_maximo": forms.TextInput(
        attrs={
          "placeholder": "Ingresar valor máximo de referencia",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "activo": forms.CheckboxInput(
        attrs={
          "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
    }

    labels = {
      "categoria_examen": "Categoría del Examen",
      "nombre": "Nombre del Examen",
      "descripcion": "Descripción del Examen",
      "valor_minimo": "Valor Mínimo",
      "valor_maximo": "Valor Máximo",
      "activo": "Examen Activo?",
    }
