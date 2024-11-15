from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.medicine import MedicineForm
from aplication.core.models import Medicamento
from doctor.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit


class MedicineListView(LoginRequiredMixin, ListViewMixin, ListView):
  template_name = "core/medicine/list.html"
  model = Medicamento
  context_object_name = 'medicamentos'

  def get_queryset(self):
    self.query = Q()
    search_query = self.request.GET.get('q')
    is_commercial = self.request.GET.get('comercial')
    is_active = self.request.GET.get('activo')

    if search_query:
      if search_query.isdigit():
        self.query.add(Q(id=search_query), Q.AND)
      else:
        self.query.add(Q(nombre__icontains=search_query) | Q(descripcion__icontains=search_query), Q.AND)

    if is_commercial in ["True", "False"]:
      self.query.add(Q(comercial=(is_commercial == "True")), Q.AND)

    if is_active in ["True", "False"]:
      self.query.add(Q(activo=(is_active == "True")), Q.AND)

    return self.model.objects.filter(self.query).order_by('nombre')


class MedicineCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
  model = Medicamento
  template_name = 'core/medicine/form.html'
  form_class = MedicineForm
  success_url = reverse_lazy('core:medicine_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['default_image_url'] = static('img/avatar_medicamento.jpg')
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear el Medicamento {objAudit.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    return self.render_to_response(self.get_context_data(form=form))


class MedicineUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
  model = Medicamento
  template_name = 'core/medicine/form.html'
  form_class = MedicineForm
  success_url = reverse_lazy('core:medicine_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['default_image_url'] = static('img/avatar_medicamento.jpg')
    context['current_image_url'] = self.object.image.url if self.object.image else static('img/avatar_medicamento.jpg')
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar el Medicamento {objAudit.nombre}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al actualizar el formulario. Corrige los errores.")
    return self.render_to_response(self.get_context_data(form=form))


class MedicineDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
  model = Medicamento
  success_url = reverse_lazy('core:medicine_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Medicamento'
    context['description'] = f"¿Desea eliminar el Medicamento: {self.object.nombre}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    messages.success(self.request, f"Éxito al eliminar lógicamente el Medicamento {self.object.nombre}.")
    return super().delete(request, *args, **kwargs)


class MedicineDetailView(LoginRequiredMixin, DetailView):
  model = Medicamento
  extra_context = {
    "detail": "Detalles del Medicamento"
  }

  def get(self, request, *args, **kwargs):
    medicamento = self.get_object()
    data = {
      'id': medicamento.id,
      'image': medicamento.get_image(),
      'tipo': medicamento.tipo.nombre,
      'marca_medicamento': medicamento.marca_medicamento.nombre,
      'nombre': medicamento.nombre,
      'descripcion': medicamento.descripcion,
      'concentracion': medicamento.concentracion,
      'cantidad': medicamento.cantidad,
      'precio': float(medicamento.precio),
      'comercial': medicamento.comercial,
      'activo': medicamento.activo,
    }
    return JsonResponse(data)
