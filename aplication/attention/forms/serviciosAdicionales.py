from django import forms
from django.forms import ModelForm

from aplication.attention.models import ServiciosAdicionales


class ServiciosAdicionalesForm(ModelForm):
  class Meta:
    model = ServiciosAdicionales
    fields = ["nombre_servicio", "costo_servicio", "descripcion", "activo"]

    error_messages = {
      "nombre_servicio": {
        "requerid": "Ingresar nombre del servicio.",
      },
    }

    widgets = {
      "nombre_servicio": forms.TextInput(
        attrs={
          "placeholder": "Ingresar nombre del servicio",
          "id": "id_nombre_servicio",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        },
      ),
      "costo_servicio": forms.NumberInput(
        attrs={
          "placeholder": "Ingresar el costo del servicio",
          "id": "id_costo_servicio",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
          "step": "0.01"
        },
      ),
      "descripcion": forms.TextInput(
        attrs={
          "placeholder": "Ingresar deacripción del servicio",
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
      "nombre_servicio": "Nombre del Servicio",
      "costo_servicio": "Costo",
      "descripcion": "Descripción",
      "activo": "Especialidad activa ?",
    }

  def clean_costo_servicio(self):
    value = self.cleaned_data.get("costo_servicio")
    if value <= 0:
      raise forms.ValidationError("Debe ingresar un número positivo en el Costo del Servicio.")
    return value
