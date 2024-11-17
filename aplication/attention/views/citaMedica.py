from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, DetailView, CreateView, UpdateView

from aplication.attention.forms.citaMedica import CitaMedicaForm
from aplication.attention.models import CitaMedica
from aplication.security.mixins.mixins import *
from doctor.const import CITA_CHOICES
from doctor.utils import save_audit


class CitaMedicaListView(PermissionMixin, ListViewMixin, ListView):
  template_name = "attention/citaMedica/list.html"
  model = CitaMedica
  context_object_name = 'citas'
  permission_required = 'view_citamedica'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # Texto de búsqueda
    estado = self.request.GET.get('estado')  # Estado de la cita

    if q1:
      # Si q1 es un número, filtrar solo por ID
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
        self.query.add(Q(paciente__cedula__icontains=q1), Q.OR)
      else:
        # Si q1 no es un número, buscar por nombres y apellidos del paciente
        self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
        self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)

    # Filtrar por estado si es uno de los valores válidos
    if estado in ["P", "C", "R"]:
      self.query.add(Q(estado=estado), Q.AND)

    # Retornar el queryset filtrado, ordenado por nombres y apellidos del paciente
    return self.model.objects.filter(self.query).order_by('paciente__nombres', 'paciente__apellidos')


class CitaMedicaCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = CitaMedica
  template_name = 'attention/citaMedica/form.html'
  form_class = CitaMedicaForm
  permission_required = 'add_citamedica'
  success_url = reverse_lazy('attention:citaMedica_list')

  def form_valid(self, form):
    try:
      # Guardar el formulario y obtener la respuesta
      response = super().form_valid(form)
      citaMedica = self.object

      # Configuración del mensaje según el estado de la cita
      estado_cita = dict(CITA_CHOICES).get(citaMedica.estado, 'Estado desconocido')
      fecha_hora_cita = f"{citaMedica.fecha} a las {citaMedica.hora_cita}"
      mensaje_sms = f"Su cita fue {estado_cita} para {fecha_hora_cita}."

      # Enviar correo electrónico
      asunto = "Cita Médica"
      mensaje_correo = f"Estimado(a) {citaMedica.paciente.nombre_completo}, su cita médica ha sido {estado_cita} para el día {fecha_hora_cita}."
      remitente = self.request.user.email
      destinatario = [citaMedica.paciente.email]
      send_mail(asunto, mensaje_correo, remitente, destinatario, fail_silently=False)

      save_audit(self.request, citaMedica, action='A')
      messages.success(self.request, f"Éxito al Crear la Cita Médica {citaMedica.paciente} - {citaMedica.estado}.")

      return response
    except ValidationError as e:
      form.add_error(None, e.message)
      return self.form_invalid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    return self.render_to_response(self.get_context_data(form=form))


class CitaMedicaUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = CitaMedica
  template_name = 'attention/citaMedica/form.html'
  form_class = CitaMedicaForm
  permission_required = 'change_citamedica'
  success_url = reverse_lazy('attention:citaMedica_list')

  def form_valid(self, form):
    try:
      response = super().form_valid(form)
      citaMedica = self.object

      # Configuración del mensaje según el estado de la cita
      estado_cita = dict(CITA_CHOICES).get(citaMedica.estado, 'Estado desconocido')
      fecha_hora_cita = f"{citaMedica.fecha} a las {citaMedica.hora_cita}"
      mensaje_actualizacion = f"Su cita fue actualizada {estado_cita}, para {fecha_hora_cita}."

      # Enviar correo electrónico
      asunto = "Actualización de Cita Médica"
      remitente = self.request.user.email
      destinatario = [citaMedica.paciente.email]
      send_mail(asunto, mensaje_actualizacion, remitente, destinatario, fail_silently=False)

      save_audit(self.request, citaMedica, action='M')
      messages.success(self.request, f"Éxito al Modificar la Cita Médica {citaMedica.paciente} - {citaMedica.estado}.")
      return response
    except ValidationError as e:
      form.add_error(None, e.message)
      return self.form_invalid(form)

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    return self.render_to_response(self.get_context_data(form=form))


class CitaMedicaDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = CitaMedica
  permission_required = 'delete_citamedica'
  success_url = reverse_lazy('attention:citaMedica_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Cita Médica'
    context['description'] = f"¿Desea Eliminar la Cita Médica: {self.object.paciente}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente la Cita Médica {self.object.paciente} - {self.object.estado}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class CitaMedicaDetailView(LoginRequiredMixin, DetailView):
  model = CitaMedica
  extra_context = {
    "detail": "Detalles de la Cita Médica"
  }

  def get(self, request, *args, **kwargs):
    citaMedica = self.get_object()
    data = {
      'id': citaMedica.id,
      'paciente': citaMedica.paciente.nombre_completo,
      'fecha': citaMedica.fecha,
      'hora_cita': citaMedica.hora_cita,
      'estado': citaMedica.get_estado_display(),
    }
    return JsonResponse(data)
