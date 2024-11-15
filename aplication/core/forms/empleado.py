from django import forms
from django.forms import ModelForm

from aplication.core.models import Empleado


class EmpleadoForm(ModelForm):
  class Meta:
    model = Empleado
    fields = [
      "cedula",
      "nombres",
      "apellidos",
      "fecha_nacimiento",
      "cargo",
      "sueldo",
      "direccion",
      "latitud",
      "longitud",
      "foto",
      "activo",
      "telefonos",
      "email",
      "curriculum",
      "firma_digital",
    ]

    error_messages = {
      "cedula": {
        "unique": "Ya existe un Empleado con esta cédula.",
      },
      "direccion": {
        "unique": "Ya existe una dirección de trabajo registrada.",
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
          "placeholder": "Ingrese la cédula",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "nombres": forms.TextInput(
        attrs={
          "placeholder": "Ingrese los nombres",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "apellidos": forms.TextInput(
        attrs={
          "placeholder": "Ingrese los apellidos",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "fecha_nacimiento": forms.DateInput(
        attrs={
          "type": "date",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"},
        format='%Y-%m-%d'),
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
      "cargo": forms.Select(
        attrs={
          "class": "cargoEmpleado shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "sueldo": forms.TextInput(
        attrs={
          "placeholder": "Ingresar sueldo del empleador",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "telefonos": forms.TextInput(
        attrs={
          "placeholder": "Ingresar número telefónico",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "email": forms.EmailInput(
        attrs={
          "placeholder": "Correo electrónico",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "curriculum": forms.ClearableFileInput(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "firma_digital": forms.ClearableFileInput(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "foto": forms.ClearableFileInput(
        attrs={
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"}),
      "activo": forms.CheckboxInput(
        attrs={
          "id": "id_activo",
          "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"}),
    }

    labels = {
      "cedula": "Cédula",
      "nombres": "Nombres",
      "apellidos": "Apellidos",
      "fecha_nacimiento": "Fecha de Nacimiento",
      "direccion": "Dirección de Trabajo",
      "latitud": "Latitud",
      "longitud": "Longitud",
      "cargo": "Cargos",
      "telefonos": "Teléfonos",
      "email": "Correo",
      "curriculum": "Curriculum Vitae",
      "firma_digital": "Firma Digital",
      "foto": "Foto",
      "activo": "Activo",
    }

  # def __init__(self, *args, **kwargs):
  #   super().__init__(*args, **kwargs)
  #   if self.instance and self.instance.pk:
  #     self.fields['fecha_nacimiento'].initial = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')
  #
  # def clean_fecha_nacimiento(self):
  #   fecha = self.cleaned_data.get('fecha_nacimiento')
  #   if fecha:
  #     return fecha.strftime('%Y-%m-%d')
  #   return fecha
