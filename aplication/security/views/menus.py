from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from aplication.security.forms.menu import MenuForm
from aplication.security.mixins.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, PermissionMixin, UpdateViewMixin
from aplication.security.models import Menu


# vista para el buscadador dinamico
class MenuSuggestionsView(ListView):
  def get(self, request, *args, **kwargs):
    term = request.GET.get('term', '')
    suggestions = Menu.objects.filter(name__icontains=term).values('icon', 'name')[
                  :10]
    suggestions_list = list(suggestions)
    return JsonResponse(suggestions_list, safe=False)


# Presentar todos los modulos
class MenuListView(PermissionMixin, ListViewMixin, ListView):
  model = Menu
  template_name = 'security/menu/list.html'
  context_object_name = 'menus'
  paginate_by = 5
  permission_required = 'view_menu'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    for menu in context['object_list']:
      menu.can_be_deleted = not menu.has_related_objects()
    return context

  def get_queryset(self):
    q1 = self.request.GET.get('q')
    if q1:
      query = Q(name__icontains=q1)
    else:
      query = Q()

    return self.model.objects.filter(query).order_by('id')


class MenuCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = Menu
  form_class = MenuForm
  template_name = 'security/menu/form.html'
  success_url = reverse_lazy('security:menus_list')
  permission_required = 'add_menu'

  def form_valid(self, form):
    response = super().form_valid(form)
    menu = self.object
    messages.success(self.request, f"Éxito al crear el menu {menu.name}.")
    return response


class MenuUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = Menu
  form_class = MenuForm
  template_name = 'security/menu/form.html'
  success_url = reverse_lazy('security:menus_list')
  permission_required = 'change_menu'

  def form_valid(self, form):
    response = super().form_valid(form)
    menu = self.object
    messages.success(self.request, f"Éxito al actualizar el menu {menu.name}.")
    return response


class MenuDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = Menu
  template_name = 'security/auth/delete.html'
  success_url = reverse_lazy('security:menus_list')
  permission_required = 'delete_menu'

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.object = None

  def delete(self, request, *args, **kwargs):
    menu = self.get_object()

    if menu.has_related_objects():
      messages.error(request, 'Este menú está relacionado con otros objetos y no puede ser eliminado.')
      return redirect(self.success_url)

    return super().delete(request, *args, **kwargs)
