from django import forms
from django.forms import ModelForm

from aplication.core.models import Doctor


class DoctorForm(ModelForm):
  horario_atencion = forms.CharField(
    widget=forms.HiddenInput(attrs={'id': 'horario_atencion_input'})
  )

  class Meta:
    model = Doctor
    fields = [
      "cedula",
      "nombres",
      "apellidos",
      "fecha_nacimiento",
      "direccion",
      "latitud",
      "longitud",
      "codigoUnicoDoctor",
      "especialidad",
      "telefonos",
      "email",
      "horario_atencion",
      "duracion_cita",
      "curriculum",
      "firmaDigital",
      "foto",
      "imagen_receta",
      "activo"
    ]

    error_messages = {
      "cedula": {
        "unique": "Ya existe un doctor con esta cédula.",
      },
      "direccion": {
        "unique": "Ya existe una dirección de trabajo registrada.",
      },
      "codigoUnicoDoctor": {
        "unique": "Ya existe un doctor con este código único.",
      },
      "email": {
        "unique": "Ya existe un correo registrado.",
      },
      "telefonos": {
        "unique": "Ya existe este teléfono.",
      },
    }

    widgets = {
      "cedula": forms.TextInput(
        attrs={
          "id": "id_cedula",
          "placeholder": "Ingrese la cédula",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "nombres": forms.TextInput(
        attrs={
          "placeholder": "Ingrese los nombres",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "apellidos": forms.TextInput(
        attrs={
          "placeholder": "Ingrese los apellidos",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "fecha_nacimiento": forms.DateInput(
        attrs={"type": "date",
               "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
               },
        format='%Y-%m-%d'
      ),
      "direccion": forms.TextInput(
        attrs={
          "placeholder": "Ingrese la dirección de trabajo",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
          "readonly": "readonly"
        },
      ),
      "latitud": forms.NumberInput(
        attrs={
          "placeholder": "Latitud",
          "step": "0.000001",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
          "readonly": "readonly"
        },
      ),
      "longitud": forms.NumberInput(
        attrs={
          "placeholder": "Longitud",
          "step": "0.000001",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
          "readonly": "readonly"
        },
      ),
      "codigoUnicoDoctor": forms.TextInput(
        attrs={
          "placeholder": "Código Único del Doctor",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "especialidad": forms.SelectMultiple(
        attrs={
          "class": "especialidadMultiple shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),

      # "especialidad": forms.CheckboxSelectMultiple(),          NO OLVIDARLA

      "telefonos": forms.TextInput(
        attrs={
          "placeholder": "Ingrese los teléfonos",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "email": forms.EmailInput(
        attrs={
          "placeholder": "Correo electrónico",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "duracion_cita": forms.NumberInput(
        attrs={
          "placeholder": "Duración de cita (minutos)",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "curriculum": forms.ClearableFileInput(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "firmaDigital": forms.ClearableFileInput(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "foto": forms.ClearableFileInput(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
        },
      ),
      "imagen_receta": forms.ClearableFileInput(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
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
      "cedula": "Cédula",
      "nombres": "Nombres",
      "apellidos": "Apellidos",
      "fecha_nacimiento": "Fecha de Nacimiento",
      "direccion": "Dirección de Trabajo",
      "latitud": "Latitud",
      "longitud": "Longitud",
      "codigoUnicoDoctor": "Código Único del Doctor",
      "especialidad": "Especialidades",
      "telefonos": "Teléfonos",
      "email": "Correo",
      "horario_atencion": "Horario de Atención",
      "duracion_cita": "Duración de Atención (minutos)",
      "curriculum": "Curriculum Vitae",
      "firmaDigital": "Firma Digital",
      "foto": "Foto",
      "imagen_receta": "Imagen para Recetas",
      "activo": "Activo",
    }
