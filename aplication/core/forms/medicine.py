from django import forms
from django.forms import ModelForm

from aplication.core.models import Medicamento


class MedicineForm(ModelForm):
  class Meta:
    model = Medicamento
    fields = [
      "image",
      "tipo",
      "marca_medicamento",
      "nombre",
      "descripcion",
      "concentracion",
      "cantidad",
      "precio",
      "comercial",
      "activo",
    ]

    error_messages = {
      "nombre": {
        "unique": "Ya existe un medicamento con este nombre.",
      },
    }

    widgets = {
      "image": forms.ClearableFileInput(
        attrs={
          "id": "id_image",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "tipo": forms.Select(
        attrs={
          "id": "id_tipo",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "marca_medicamento": forms.Select(
        attrs={
          "id": "id_marca_medicamento",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "nombre": forms.TextInput(
        attrs={
          "placeholder": "Ingresar el nombre del medicamento",
          "id": "id_nombre",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "descripcion": forms.TextInput(
        attrs={
          "placeholder": "Ingresar la descripción del medicamento",
          "id": "id_descripcion",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
          "rows": 3,
        }
      ),
      "concentracion": forms.TextInput(
        attrs={
          "placeholder": "Ingresar la concentración del medicamento",
          "id": "id_concentracion",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "cantidad": forms.NumberInput(
        attrs={
          "placeholder": "Cantidad en stock",
          "id": "id_cantidad",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "precio": forms.NumberInput(
        attrs={
          "placeholder": "Precio del medicamento",
          "id": "id_precio",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "comercial": forms.CheckboxInput(
        attrs={
          "id": "id_comercial",
          "class": "checkbox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
      "activo": forms.CheckboxInput(
        attrs={
          "id": "id_activo",
          "class": "checkbox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
        }
      ),
    }

    labels = {
      "image": "Foto del Medicamento",
      "tipo": "Tipo de Medicamento",
      "marca_medicamento": "Marca del Medicamento",
      "nombre": "Nombre del Medicamento",
      "descripcion": "Descripción",
      "concentracion": "Concentración",
      "cantidad": "Cantidad en Stock",
      "precio": "Precio",
      "comercial": "Es Comercial?",
      "activo": "Activo?",
    }
