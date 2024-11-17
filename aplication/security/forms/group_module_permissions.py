from django import forms

from aplication.security.models import GroupModulePermission


class GroupModulePermissionForm(forms.ModelForm):
  class Meta:
    model = GroupModulePermission
    fields = ['group']
    widgets = {
      'group': forms.Select(attrs={
        'class': 'selectGrups',
      })}
    labels = {
      'group': 'Grupo',
    }
