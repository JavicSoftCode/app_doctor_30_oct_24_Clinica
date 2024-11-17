from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from aplication.attention.forms.examenSolicitado import ExamenSolicitadoForm
from aplication.attention.models import ExamenSolicitado
from doctor.utils import save_audit
from aplication.security.mixins.mixins import *


class ExamenSolicitadoListView(PermissionMixin, ListViewMixin, ListView):
  template_name = "attention/examenSolicitado/list.html"
  model = ExamenSolicitado
  permission_required = 'view_examensolicitado'
  context_object_name = 'examenes'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    estado = self.request.GET.get('estado')

    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
      else:
        self.query.add(Q(nombre_examen__icontains=q1), Q.OR)
        # self.query.add(Q(paciente__cedula__icontains=q1), Q.OR)
        self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
        self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)

    # Filtrar por estado si es uno de los valores válidos
    if estado in ["S", "R"]:
      self.query.add(Q(estado=estado), Q.AND)

    # Retornar el queryset filtrado, ordenado por nombres y apellidos del paciente
    return self.model.objects.filter(self.query).order_by('paciente__nombres', 'paciente__apellidos')


class ExamenSolicitadoCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = ExamenSolicitado
  template_name = 'attention/examenSolicitado/form.html'
  form_class = ExamenSolicitadoForm
  permission_required = 'add_examensolicitado'
  success_url = reverse_lazy('attention:examenSolicitado_list')

  def form_valid(self, form):
    # print("entro al form_valid")
    response = super().form_valid(form)
    examenSolicitado = self.object
    save_audit(self.request, examenSolicitado, action='A')
    messages.success(self.request, f"Éxito al crear el Exámen Solicitado {examenSolicitado.nombre_examen}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class ExamenSolicitadoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = ExamenSolicitado
  template_name = 'attention/examenSolicitado/form.html'
  form_class = ExamenSolicitadoForm
  permission_required = 'change_examensolicitado'
  success_url = reverse_lazy('attention:examenSolicitado_list')

  def form_valid(self, form):
    response = super().form_valid(form)
    examenSolicitado = self.object
    save_audit(self.request, examenSolicitado, action='M')
    messages.success(self.request, f"Éxito al Modificar el Exámen Solicitado {examenSolicitado.nombre_examen}.")
    print("mande mensaje")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class ExamenSolicitadoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = ExamenSolicitado
  permission_required = 'delete_examensolicitado'
  success_url = reverse_lazy('attention:examenSolicitado_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['grabar'] = 'Eliminar Exámen Solicitado'
    context['description'] = f"¿Desea Eliminar la Exámen Solicitado: {self.object.nombre_examen}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    examenSolicitado = self.object.nombre_examen
    # Guarda la auditoría de la eliminación
    save_audit(self.request, self.object, action='E')

    success_message = f"Éxito al eliminar lógicamente el Examen Solicitado {examenSolicitado}."
    messages.success(self.request, success_message)

    return super().delete(request, *args, **kwargs)


class ExamenSolicitadoDetailView(LoginRequiredMixin, DetailView):
  model = ExamenSolicitado
  extra_context = {
    "detail": "Detalles del Exámen Solicitado"
  }

  def get(self, request, *args, **kwargs):
    examenSolicitado = self.get_object()
    data = {
      'id': examenSolicitado.id,
      'nombre_examen': examenSolicitado.nombre_examen,
      'paciente': examenSolicitado.paciente.nombre_completo,
      'foto': examenSolicitado.paciente.get_image(),
      'fecha_solicitud': examenSolicitado.fecha_solicitud.isoformat() if examenSolicitado.fecha_solicitud else None,
      'resultado': examenSolicitado.resultado.url if examenSolicitado.resultado else None,
      'comentario': examenSolicitado.comentario,
      'estado': examenSolicitado.estado,
    }
    return JsonResponse(data)
