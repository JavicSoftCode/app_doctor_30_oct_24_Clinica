from django import forms
from django.contrib.auth.models import User, Group


class UserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'groups']


class UserGroupForm(forms.ModelForm):
  groups = forms.ModelMultipleChoiceField(
    queryset=Group.objects.all(),
    widget=forms.CheckboxSelectMultiple(attrs={
      "class": "checo",
    }),
    required=False,
    label="Grupos"
  )

  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'username', 'email', 'is_active', 'is_staff', 'groups', 'is_superuser']

  widgets = {
    "first_name": forms.TextInput(
      attrs={
        "placeholder": "Ingresar nombres",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        "readonly": "readonly", }),
    "last_name": forms.TextInput(
      attrs={
        "placeholder": "Ingresar apellidos",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        "readonly": "readonly", }),
    "username": forms.TextInput(
      attrs={
        "placeholder": "Ingresar nombre de usuario",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        "readonly": "readonly", }),
    "email": forms.EmailInput(
      attrs={
        "placeholder": "Ingresar correo electrónico",
        "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
        "readonly": "readonly", }),
    "is_active": forms.CheckboxInput(
      attrs={
        "id": "id_is_active",
        "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"}),
    "is_staff": forms.CheckboxInput(
      attrs={
        "id": "id_is_staff",
        "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"}),
    "is_superuser": forms.CheckboxInput(
      attrs={
        "id": "id_is_superuser",
        "class": "checkox shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"}),
  }

  labels = {
    "first_name": "Nombres",
    "last_name": "Apellidos",
    "username": "Correo",
    "email": "Correo",
    "is_active": "Activo",
    "is_staff": "Administrador",
    "is_superuser": "Super Usuario",
  }
