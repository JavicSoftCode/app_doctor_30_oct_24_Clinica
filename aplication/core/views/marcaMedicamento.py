from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.marcaMedicamento import MarcaMedicamentoForm
from aplication.core.models import MarcaMedicamento
from aplication.security.mixins.mixins import *
from doctor.utils import save_audit


class MarcaMedicamentoListView(PermissionMixin, ListViewMixin, ListView):
  template_name = "core/marcaMedicamento/list.html"
  model = MarcaMedicamento
  permission_required = 'view_marcamedicamento'
  context_object_name = 'marcas'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    activo = self.request.GET.get('activo')

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
      else:
        self.query.add(Q(nombre__icontains=q1), Q.AND)

    if activo in ["True", "False"]:
      is_active = activo == "True"
      self.query.add(Q(activo=is_active), Q.AND)
    return self.model.objects.filter(self.query).order_by('nombre')


class MarcaMedicamentoCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = MarcaMedicamento
  template_name = 'core/marcaMedicamento/form.html'
  form_class = MarcaMedicamentoForm
  permission_required = 'add_marcamedicamento'
  success_url = reverse_lazy('core:marcaMedicamento_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    marcaM = self.object
    save_audit(self.request, marcaM, action='A')
    messages.success(self.request, f"Éxito al crear la Marca Medicamento {marcaM.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class MarcaMedicamentoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = MarcaMedicamento
  template_name = 'core/marcaMedicamento/form.html'
  form_class = MarcaMedicamentoForm
  permission_required = 'change_marcamedicamento'
  success_url = reverse_lazy('core:marcaMedicamento_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    marcaM = self.object
    save_audit(self.request, marcaM, action='M')
    messages.success(self.request, f"Éxito al Modificar la Marca Medicamento {marcaM.nombre}.")
    print("mande mensaje")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class MarcaMedicamentoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = MarcaMedicamento
  permission_required = 'delete_marcamedicamento'
  success_url = reverse_lazy('core:marcaMedicamento_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['grabar'] = 'Eliminar Marca Medicamento'
    context['description'] = f"¿Desea Eliminar la Marca Medicamento: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    if self.object.tiene_relaciones:
      messages.error(self.request,
                     "No se puede eliminar la marca del medicamento porque tiene relación con Medicamentos.")
      return redirect(self.success_url)
    specialty_name = self.object.nombres
    save_audit(self.request, self.object, action='E')
    success_message = f"Éxito al eliminar lógicamente la Marca Medicamento {specialty_name}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class MarcaMedicamentoDetailView(LoginRequiredMixin, DetailView):
  model = MarcaMedicamento
  extra_context = {
    "detail": "Detalles de la Marca Medicamento"
  }

  def get(self, request, *args, **kwargs):
    marcaM = self.get_object()
    data = {
      'id': marcaM.id,
      'nombre': marcaM.nombre,
      'descripcion': marcaM.descripcion,
      'activo': marcaM.activo,
    }
    return JsonResponse(data)
