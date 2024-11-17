from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View

from aplication.security.forms.user import UserGroupForm
from aplication.security.mixins.mixins import *

# from aplication.security.models import User

User = get_user_model()


class UsersListView(PermissionRequiredMixin, ListViewMixin, ListView):
  template_name = 'security/usuarios/list.html'
  model = User
  context_object_name = 'users'
  paginate_by = 5
  permission_required = 'auth.view_user'

  def get_queryset(self):
    queryset = super().get_queryset().prefetch_related('groups').filter(is_superuser=False)
    q = self.request.GET.get('q')
    if q:
      queryset = queryset.filter(username__icontains=q)
    return queryset.order_by('id')

  # def get_context_data(self, **kwargs):
  #   context = super().get_context_data(**kwargs)
  #   context['title1'] = 'Usuarios Con Roles'
  #   context['title2'] = 'Consulta Usuarios Con Roles'
  #   context['create_url'] = reverse_lazy('security:users_create')
  #   return context


class UserCreateView(PermissionRequiredMixin, CreateViewMixin, CreateView):
  model = User
  form_class = UserGroupForm
  template_name = 'security/usuarios/form.html'
  success_url = reverse_lazy('security:users_list')
  permission_required = 'auth.add_user'

  # def get_context_data(self, **kwargs):
  #   context = super().get_context_data(**kwargs)
  #   context['title1'] = 'Usuarios Con Roles'
  #   context['title2'] = 'Actualizar Roles'
  #   context['create_url'] = reverse_lazy('security:users_list')
  #   return context

  def form_valid(self, form):
    response = super().form_valid(form)
    user = self.object
    messages.success(self.request, f"Éxito al crear el usuario {user.username}.")
    return response


class UserUpdateView(PermissionRequiredMixin, UpdateViewMixin, UpdateView):
  model = User
  form_class = UserGroupForm
  template_name = 'security/usuarios/form.html'
  success_url = reverse_lazy('security:users_list')
  permission_required = 'auth.change_user'

  def form_valid(self, form):
    response = super().form_valid(form)
    user = self.object
    messages.success(self.request, f"Éxito al actualizar el usuario {user.username}.")
    return response


class UserDeleteView(PermissionRequiredMixin, DeleteViewMixin, DeleteView):
  model = User
  template_name = 'security/auth/delete.html'
  success_url = reverse_lazy('security:users_list')
  permission_required = 'auth.delete_user'

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar el usuario {self.object.username}."
    self.object.delete()
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class UserGroupView(View):

  def get(self, request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = UserGroupForm(instance=user)
    return render(request, 'security/usuarios/form.html', {'form': form, 'title': 'Asignar/Quitar Grupos'})

  def post(self, request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = UserGroupForm(request.POST, instance=user)
    if form.is_valid():
      form.save()
      messages.success(self.request, f"Éxito al actualizar los grupos del usuario {user.username}.")
      return redirect('security:users_list')
    return render(request, 'security/usuarios/form.html', {'form': form, 'title': 'Asignar/Quitar Grupos'})
