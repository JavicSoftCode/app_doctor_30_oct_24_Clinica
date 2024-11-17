from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.cargo import CargoForm
from aplication.core.models import Cargo
from aplication.security.mixins.mixins import *
from doctor.utils import save_audit


class CargoListView(PermissionMixin, ListViewMixin, ListView):
  template_name = "core/cargo/list.html"
  model = Cargo
  context_object_name = 'cargos'
  permission_required = 'view_cargo'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    cargo = self.request.GET.get('cargo')

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      else:
        self.query.add(Q(nombre__icontains=q1), Q.AND)

    if cargo in ["True", "False"]:
      is_active = cargo == "True"
      self.query.add(Q(activo=is_active), Q.AND)
    return self.model.objects.filter(self.query).order_by('nombre')


class CargoCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = Cargo
  template_name = 'core/cargo/form.html'
  form_class = CargoForm
  permission_required = 'add_cargo'
  success_url = reverse_lazy('core:cargo_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear el Cargo {objAudit.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CargoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = Cargo
  template_name = 'core/cargo/form.html'
  form_class = CargoForm
  permission_required = 'change_cargo'
  success_url = reverse_lazy('core:cargo_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar el Cargo {objAudit.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class CargoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = Cargo
  permission_required = 'delete_cargo'

  success_url = reverse_lazy('core:cargo_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Cargo'
    context['description'] = f"¿Desea Eliminar el Cargo: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()

    if self.object.tiene_relaciones:
      messages.error(self.request, "No se puede eliminar el cargo porque está en uso.")
      return redirect(self.success_url)

    success_message = f"Éxito al eliminar lógicamente el Cargo {self.object.nombre}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class CargoDetailView(LoginRequiredMixin, DetailView):
  model = Cargo
  extra_context = {
    "detail": "Detalles del Cargo"
  }

  def get(self, request, *args, **kwargs):
    cargo = self.get_object()
    data = {
      'id': cargo.id,
      'nombre': cargo.nombre,
      'descripcion': cargo.descripcion,
      'activo': cargo.activo,
    }
    return JsonResponse(data)
