from django import forms
from django.forms import ModelForm

from aplication.security.models import Module


class ModuleForm(ModelForm):
  class Meta:
    model = Module
    fields = ['url', 'name', 'menu', 'description', 'icon', 'is_active', 'permissions']
    labels = {
      "url": "Url",
      "name": "Nombre",
      "menu": "Menú",
      "description": "Descripción",
      "icon": "Icono",
      "is_active": "Activo",
      "permissions": "Permisos",
    }
    error_messages = {
      "url": {
        "unique": "Ya existe un módulo con esta URL.",
      },
      "name": {
        "unique": "Ya existe un módulo con este nombre.",
      },
    }
    widgets = {
      "url": forms.TextInput(attrs={
        "placeholder": "Ingrese URL del módulo",
        "id": "id_url",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "name": forms.TextInput(attrs={
        "placeholder": "Ingrese nombre del módulo",
        "id": "id_name",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "menu": forms.Select(attrs={
        "id": "id_menu",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "description": forms.TextInput(attrs={
        "placeholder": "Ingrese descripción del módulo",
        "id": "id_description",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "icon": forms.TextInput(attrs={
        "placeholder": "Ingrese icono del módulo",
        "id": "id_icon",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "is_active": forms.CheckboxInput(attrs={
        "class": "mt-1 block px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      }),
      "permissions": forms.CheckboxSelectMultiple(attrs={
        "class": "checo",
      }),
    }

  def clean_name(self):
    name = self.cleaned_data.get("name")
    return name.upper()
