from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.core.forms.diagnosis import DiagnosisForm
from aplication.core.models import Diagnostico
from doctor.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit


class DiagnosisListView(LoginRequiredMixin, ListViewMixin, ListView):
  template_name = "core/diagnosis/list.html"
  model = Diagnostico
  context_object_name = 'diagnosticos'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    diagnosis = self.request.GET.get('diagnostico')

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
      else:
        self.query.add(Q(codigo__icontains=q1), Q.AND)

    if diagnosis in ["True", "False"]:
      is_active = diagnosis == "True"
      self.query.add(Q(activo=is_active), Q.AND)
    return self.model.objects.filter(self.query).order_by('descripcion')


class DiagnosisCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
  model = Diagnostico
  template_name = 'core/diagnosis/form.html'
  form_class = DiagnosisForm
  success_url = reverse_lazy('core:diagnosis_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear el Diagnostico {objAudit.codigo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class DiagnosisUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
  model = Diagnostico
  template_name = 'core/diagnosis/form.html'
  form_class = DiagnosisForm
  success_url = reverse_lazy('core:diagnosis_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar el Diagnostico {objAudit.codigo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class DiagnosisDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
  model = Diagnostico
  success_url = reverse_lazy('core:diagnosis_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Diagnostico'
    context['description'] = f"¿Desea Eliminar el Diagnostico: {self.object.codigo}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente el Diagnostico {self.object.codigo}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class DiagnosisDetailView(LoginRequiredMixin, DetailView):
  model = Diagnostico
  extra_context = {
    "detail": "Detalles del Diagnostico"
  }

  def get(self, request, *args, **kwargs):
    diagnosis = self.get_object()
    data = {
      'id': diagnosis.id,
      'codigo': diagnosis.codigo,
      'descripcion': diagnosis.descripcion,
      'datos_adicionales': diagnosis.datos_adicionales,
      'activo': diagnosis.activo,
    }
    return JsonResponse(data)
