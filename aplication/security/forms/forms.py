from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from aplication.security.models import User
from django.db import models
from django.forms import ImageField, FileInput
from django.contrib.auth.forms import PasswordChangeForm


class CustomUserCreationForm(UserCreationForm):
  dni = forms.CharField(max_length=10, label="DNI")
  first_name = forms.CharField(max_length=30, label="Nombres")
  last_name = forms.CharField(max_length=150, label="Apellidos")
  phone = forms.CharField(max_length=10, required=False, label="Celular")
  email = forms.EmailField(required=True, label="Correo electrónico")
  image = forms.ImageField(required=False, label="Foto de perfil", widget=FileInput(attrs={
    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
  }))

  class Meta(UserCreationForm.Meta):
    model = User
    fields = [
      "username",
      "first_name",
      "last_name",
      "dni",
      "phone",
      "email",
      "image",
      "password1",
      "password2",
    ]


class CustomUserUpdateForm(UserChangeForm):
  password = None
  image = ImageField(widget=FileInput(attrs={
    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
  }))

  class Meta:
    model = User
    fields = ["first_name", "last_name", "dni", "phone", "email", "image"]
    labels = {
      "first_name": "Nombres",
      "last_name": "Apellidos",
      "dni": "DNI o Ruc",
      "phone": "Celular",
      "email": "Correo electrónico",
      "image": "Imagen",
    }
    error_messages = {
      "dni": {
        "unique": "Ya existe un usuario con este DNI.",
      },
      "phone": {
        "unique": "Ya existe un usuario con este número de celular.",
      },
      "email": {
        "unique": "Ya existe un usuario con este correo electrónico.",
      },
    }
    widgets = {
      "first_name": forms.TextInput(attrs={
        "placeholder": "Ingrese nombres del usuario",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "last_name": forms.TextInput(attrs={
        "placeholder": "Ingrese apellidos del usuario",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "dni": forms.TextInput(attrs={
        "placeholder": "Ingrese DNI del usuario",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "phone": forms.TextInput(attrs={
        "placeholder": "Ingrese número celular del usuario",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
      }),
      "email": forms.EmailInput(
        attrs={
          "placeholder": "Ingrese correo electrónico del usuario",
          "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        }),
    }


class CustomPasswordChangeForm(PasswordChangeForm):
  class Meta:
    fields = ["old_password", "new_password1", "new_password2"]
    labels = {
      "old_password": "Contraseña actual",
      "new_password1": "Nueva contraseña",
      "new_password2": "Confirma la nueva contraseña",
    }
    widgets = {
      "old_password": forms.PasswordInput(attrs={
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        "placeholder": "Contraseña actual"
      }),
      "new_password1": forms.PasswordInput(attrs={
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        "placeholder": "Nueva contraseña"
      }),
      "new_password2": forms.PasswordInput(attrs={
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
        "placeholder": "Confirma la nueva contraseña"
      }),
    }
