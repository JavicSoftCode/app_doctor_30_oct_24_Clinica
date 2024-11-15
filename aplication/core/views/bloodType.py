from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.bloodType import BloodTypeForm
from aplication.core.models import TipoSangre
from doctor.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit


class BloodTypeListView(LoginRequiredMixin, ListViewMixin, ListView):
  template_name = "core/bloodType/list.html"
  model = TipoSangre
  context_object_name = 'tipos_sangre'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    tipoSangre = self.request.GET.get('tip')
    if q1 is not None:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
      else:
        self.query.add(Q(tipo__icontains=q1), Q.OR)
    if tipoSangre == "+" or tipoSangre == "-": self.query.add(Q(tipo__icontains=tipoSangre), Q.AND)
    return self.model.objects.filter(self.query).order_by('tipo')


class BloodTypeCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
  model = TipoSangre
  template_name = 'core/bloodType/form.html'
  form_class = BloodTypeForm
  success_url = reverse_lazy('core:bloodType_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    bloodType = self.object
    save_audit(self.request, bloodType, action='A')
    messages.success(self.request, f"Éxito al crear el Tipo de Sangre {bloodType.tipo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class BloodTypeUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
  model = TipoSangre
  template_name = 'core/bloodType/form.html'
  form_class = BloodTypeForm
  success_url = reverse_lazy('core:bloodType_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    bloodType = self.object
    save_audit(self.request, bloodType, action='M')
    messages.success(self.request, f"Éxito al Modificar el Tipo de Sangre {bloodType.tipo}.")
    print("mande mensaje")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class BloodTypeDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
  model = TipoSangre
  success_url = reverse_lazy('core:bloodType_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Tipo de Sangre'
    context['description'] = f"¿Desea Eliminar el Tipo de Sangre: {self.object.descripcion}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente el Tipo de Sangre {self.object.descripcion}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs), bloodType


class BloodTypeDetailView(LoginRequiredMixin, DetailView):
  model = TipoSangre
  extra_context = {
    "detail": "Detalles Tipo Sangre"
  }

  def get(self, request, *args, **kwargs):
    bloodType = self.get_object()
    data = {
      'id': bloodType.id,
      'tipo': bloodType.tipo,
      'descripcion': bloodType.descripcion,
    }
    return JsonResponse(data)
