from django import forms
from django.forms import ModelForm

from aplication.attention.models import ExamenSolicitado


class ExamenSolicitadoForm(ModelForm):
  class Meta:
    model = ExamenSolicitado
    fields = ["nombre_examen", "paciente", "resultado", "comentario", "estado"]

    error_messages = {
      "nombre_examen": {
        "required": "Ingresar nombre del exámen.",
      },
      "paciente": {
        "required": "Selecionar paciente.",
      },
      "resultado": {
        "required": "Ingresar el exámen en PDF.",
      },
      "estado": {
        "required": "Selecione el estado del examen.",
      },
    }

    widgets = {
      "nombre_examen": forms.TextInput(
        attrs={
          "placeholder": "Ingresar nombre del exámen.",
          "id": "id_nombre_examen",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }
      ),
      "paciente": forms.Select(
        attrs={
          # "placeholder": "Ingresar especialidad",
          "id": "id_paciente",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }
      ),
      # "fecha_solicitud": forms.DateInput(
      #   attrs={
      #     "placeholder": "Seleccionar la fecha de solicitud del exámen",
      #     "id": "id_fecha_solicitud",
      #     "type": "date",  # Este tipo permite el selector de fechas en navegadores modernos
      #     "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      #   }
      # ),
      "resultado": forms.ClearableFileInput(
        attrs={
          # "id": "id_resultado",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        }
      ),
      "comentario": forms.TextInput(
        attrs={
          "placeholder": "Ingresar comentario ( Opcional ).",
          "id": "id_comentario",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }
      ),
      "estado": forms.Select(
        attrs={
          # "placeholder": "Ingresar la descripción",
          "id": "id_estado",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }
      ),

    }
    labels = {
      "nombre_examen": "Exámen Solicitado",
      "paciente": "Paciente",
      # "fecha_solicitud": "Fecha del Exámen Solicitado",
      "resultado": "Resultado del Exámen",
      "comentario": "Comentario",
      "estado": "Cita Médica"
    }
