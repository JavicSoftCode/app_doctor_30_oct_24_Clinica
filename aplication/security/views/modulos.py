from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views.generic import TemplateView

from aplication.security.forms.modules import ModuleForm
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, \
  UpdateViewMixin
from aplication.security.models import Module, Menu, GroupModulePermission


# vista para el buscadador dinamico
class ModuleSuggestionsView(ListView):
  def get(self, request, *args, **kwargs):
    term = request.GET.get('term', '')
    suggestions = Module.objects.filter(name__icontains=term).values('icon', 'name')[
                  :10]
    suggestions_list = list(suggestions)
    return JsonResponse(suggestions_list, safe=False)


class ModuloTemplateView(PermissionMixin, TemplateView):
  template_name = 'components/modulos.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["title1"] = "IC - Modulos"
    context["title2"] = "Modulos Disponibles"

    user = self.request.user
    group = user.get_group_session()  # Asumimos que hay un método que obtiene el grupo

    menu_list = []
    menus = Menu.objects.all().order_by('name')  # Obtener todos los menús ordenados por nombre

    for menu in menus:
      # Verificamos si el usuario es superusuario
      if user.is_superuser:
        # Si es superusuario, no filtramos por grupo
        group_module_permissions = GroupModulePermission.objects.filter(module__menu=menu).select_related('module', 'group')
      else:
        # Si no es superusuario, filtramos por el grupo del usuario
        group_module_permissions = GroupModulePermission.objects.filter(
          group=group,  # Filtramos por el grupo que tiene el usuario
          module__menu=menu  # Filtramos por los módulos asociados al menú
        ).select_related('module', 'group')

      # Solo agregamos a la lista si hay permisos asociados a este grupo para este menú
      if group_module_permissions.exists():
        menu_list.append({
          'menu': menu,
          'group_module_permission_list': group_module_permissions
        })

    context['menu_list'] = menu_list
    print("Menu list final:", menu_list)  # Debugging
    return context


class ModuleListView(PermissionMixin, ListViewMixin, ListView):
  template_name = 'security/modulos/list.html'
  model = Module
  context_object_name = 'modules'
  permission_required = 'view_modules'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    for module in context['object_list']:
      module.can_be_deleted = not module.has_related_objects_Modules()
    return context

  def get_queryset(self):
    q1 = self.request.GET.get('q')
    if q1:
      query = Q(name__icontains=q1)
    else:
      query = Q(is_active=True)

    return self.model.objects.filter(query).order_by('id')


class ModuleCreateView(PermissionMixin, CreateViewMixin, CreateView):
  template_name = 'security/modulos/form.html'
  model = Module
  form_class = ModuleForm
  success_url = reverse_lazy('security:modules_list')
  permission_required = 'add_module'

  def form_valid(self, form):
    response = super().form_valid(form)
    module = self.object
    messages.success(self.request, f"Éxito al crear el módulo {module.name}.")
    return response


class ModuleUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = Module
  template_name = 'security/modulos/form.html'
  form_class = ModuleForm
  success_url = reverse_lazy('security:modules_list')
  permission_required = 'change_module'

  def form_valid(self, form):
    response = super().form_valid(form)
    module = self.object
    messages.success(self.request, f"Éxito al actualizar el módulo {module.name}.")
    return response


class ModuleDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = Module
  template_name = 'fragments/delete.html'
  success_url = reverse_lazy('security:modules_list')
  permission_required = 'delete_module'

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()

    # Verificar si existen relaciones con otros objetos
    if self.object.groupmodulepermission_set.exists():
      # Mostrar mensaje de error
      messages.error(request, "No se puede eliminar el módulo porque tiene relaciones con otros objetos.")
      return redirect(reverse('security:modules_list'))

    # Eliminación física del objeto Module
    success_url = self.get_success_url()
    self.object.delete()
    return redirect(success_url)
