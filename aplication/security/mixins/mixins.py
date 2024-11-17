from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from aplication.security.instance.group_permission import GroupPermission
from aplication.security.instance.menu_module import MenuModule


class ListViewMixin(object):
  query = None
  paginate_by = 5

  def dispatch(self, request, *args, **kwargs):
    self.query = Q()
    return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # context['title1'] = f'{self.model._meta.verbose_name_plural}'
    # context['title2'] = f'Consulta de {self.model._meta.verbose_name_plural}'

    context['title'] = "SaludSync"
    context['title1'] = f'Consulta de {self.model._meta.verbose_name_plural}'
    context['title2'] = f'Nuevo {self.model._meta.verbose_name}'

    # seguridad de grupos, modulos y permisos
    context['permissions'] = self._get_permission_dict_of_group()
    MenuModule(self.request).fill(context)
    context = self.make_context_serializable(context)
    return context

  def _get_permission_dict_of_group(self):
    return GroupPermission.get_permission_dict_of_group(self.request.user)

  def make_context_serializable(self, context):
    """Convierte los objetos no serializables en un formato serializable (por ejemplo, diccionarios)"""
    # Convertir 'group_list' si es un QuerySet o lista de objetos Group
    if 'group_list' in context and isinstance(context['group_list'], (list, Q)):
      context['group_list'] = [
        {'id': group.id, 'name': group.name} for group in context['group_list'] if isinstance(group, Group)
      ]

    # Convertir 'group' si es un objeto Group individual
    if 'group' in context and isinstance(context['group'], Group):
      context['group'] = {'id': context['group'].id, 'name': context['group'].name}

    return context


class CreateViewMixin(object):
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # context['title'] = f'{self.model._meta.verbose_name}'
    # context['title2'] = f'Registrar {self.model._meta.verbose_name}'

    context['title'] = "SaludSync"
    context['title1'] = f'Registro de {self.model._meta.verbose_name}'
    context['grabar'] = f'Guardar {self.model._meta.verbose_name}'
    context['back_url'] = self.success_url

    # seguridad de grupos, modulos y permisos
    context['permissions'] = self._get_permission_dict_of_group()
    MenuModule(self.request).fill(context)
    context = self.make_context_serializable(context)
    return context

  def _get_permission_dict_of_group(self):
    return GroupPermission.get_permission_dict_of_group(self.request.user)

  def make_context_serializable(self, context):
    """Convierte objetos no serializables en serializables"""
    if 'group' in context and isinstance(context['group'], Group):
      context['group'] = {'id': context['group'].id, 'name': context['group'].name}
    return context


class UpdateViewMixin(object):
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # context['title'] = f'{self.model._meta.verbose_name_plural}'
    # context['title2'] = f'Actualizar {self.model._meta.verbose_name}'

    context['title'] = "SaludSync"
    context['title1'] = f'Modificar {self.model._meta.verbose_name}'
    context['grabar'] = f'Actualizar {self.model._meta.verbose_name}'
    context['back_url'] = self.success_url

    # seguridad de grupos, modulos y permisos
    context['permissions'] = self._get_permission_dict_of_group()
    MenuModule(self.request).fill(context)
    context = self.make_context_serializable(context)
    return context

  def _get_permission_dict_of_group(self):
    return GroupPermission.get_permission_dict_of_group(self.request.user)

  def make_context_serializable(self, context):
    """Convierte objetos no serializables en serializables"""
    if 'group' in context and isinstance(context['group'], Group):
      context['group'] = {'id': context['group'].id, 'name': context['group'].name}
    return context


class DeleteViewMixin(object):
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # context['title'] = f'{self.model._meta.verbose_name_plural}'

    # seguridad de grupos, modulos y permisos
    context['permissions'] = self._get_permission_dict_of_group()
    MenuModule(self.request).fill(context)
    context = self.make_context_serializable(context)
    return context

  def _get_permission_dict_of_group(self):
    return GroupPermission.get_permission_dict_of_group(self.request.user)

  def make_context_serializable(self, context):
    """Convierte objetos no serializables en serializables"""
    if 'group' in context and isinstance(context['group'], Group):
      context['group'] = {'id': context['group'].id, 'name': context['group'].name}
    return context


class PermissionMixin(object):
  permission_required = ''
  print("entro al permission")

  @method_decorator(login_required)
  def get(self, request, *args, **kwargs):
    try:
      user = request.user
      user.set_group_session()

      if 'group_id' not in request.session:
        return redirect('core:home')

      if user.is_superuser:
        return super().get(request, *args, **kwargs)

      group = user.get_group_session()
      permissions = self._get_permissions_to_validate()

      if not permissions.__len__():
        return super().get(request, *args, **kwargs)

      if not group.groupmodulepermission_set.filter(
        permissions__codename__in=permissions
      ).exists():
        print("no tengo permiso")
        messages.error(request, 'No tiene permiso para ingresar a este módulo')
        return redirect('core:home')

      return super().get(request, *args, **kwargs)

    except Exception as ex:
      messages.error(
        request,
        'A ocurrido un error al ingresar al modulo, error para el admin es : {}'.format(ex))

    if request.user.is_authenticated:
      return redirect('core:home')

    return redirect('security:auth_login')

  def _get_permissions_to_validate(self):

    if self.permission_required == '':
      return ()

    if isinstance(self.permission_required, str):
      return self.permission_required,

    return tuple(self.permission_required)
