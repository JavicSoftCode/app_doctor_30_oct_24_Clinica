import json

import folium
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from folium.plugins import FastMarkerCluster

from aplication.core.forms.doctor import DoctorForm
from aplication.core.models import Doctor
from aplication.security.mixins.mixins import *
from doctor.utils import save_audit


class DoctorListView(PermissionMixin, ListViewMixin, ListView):
  template_name = "core/doctor/list.html"
  model = Doctor
  permission_required = 'view_doctor'
  context_object_name = 'doctores'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    doct = self.request.GET.get('doctor')
    if q1 is not None:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      self.query.add(Q(nombres__icontains=q1), Q.OR)
      self.query.add(Q(apellidos__icontains=q1), Q.OR)
      self.query.add(Q(cedula__icontains=q1), Q.OR)
      self.query.add(Q(codigoUnicoDoctor__icontains=q1), Q.OR)
      self.query.add(Q(email__icontains=q1), Q.OR)
      if doct in ["True", "False"]:
        is_active = doct == "True"
        self.query.add(Q(activo=is_active), Q.AND)
    return self.model.objects.filter(self.query).order_by('apellidos')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    locations = self.get_queryset()

    locations_data = [
      {
        'latitude': float(location.latitud) if location.latitud else None,
        'longitude': float(location.longitud) if location.longitud else None,
        'doctor': location.nombre_completo,
        'address': location.direccion,
        'image': location.foto.url if location.foto else static('img/doctor_avatar.webp'),
      }
      for location in locations
      if location.latitud and location.longitud  # Solo incluir doctores con coordenadas válidas
    ]
    # Convertir a JSON de manera segura
    context['locations'] = json.dumps(locations_data, cls=DjangoJSONEncoder)
    return context


class DoctorCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = Doctor
  template_name = 'core/doctor/form.html'
  form_class = DoctorForm
  permission_required = 'add_doctor'
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()

    # Mapa inicial centrado
    initial_map = folium.Map(location=[-2.129896, -79.593256], zoom_start=14)
    doctores = Doctor.objects.all()

    # Coordenadas de doctores existentes
    latitudes = [doctore.latitud for doctore in doctores]
    longitudes = [doctore.longitud for doctore in doctores]
    popups = [f"<b>{doctore.nombres} {doctore.apellidos}</b><br>{doctore.direccion}" for doctore in doctores]

    FastMarkerCluster(data=list(zip(latitudes, longitudes, popups))).add_to(initial_map)

    for doctore in doctores:
      folium.Marker(
        location=[doctore.latitud, doctore.longitud],
        popup=f"<b>{doctore.nombres} {doctore.apellidos}</b><br>{doctore.direccion}",
        icon=folium.Icon(icon='user', prefix='fa')
      ).add_to(initial_map)

    context['map'] = initial_map._repr_html_()
    context['default_image_url'] = static('img/doctor_avatar.webp')
    context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear al Doctor {objAudit.nombre_completo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class DoctorUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = Doctor
  template_name = 'core/doctor/form.html'
  form_class = DoctorForm
  permission_required = 'change_doctor'
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()

    doctor = self.object
    doctores = Doctor.objects.exclude(id=doctor.id)  # Excluir doctor actual

    # Preparar datos de ubicación de otros doctores
    doctores_locations = [
      {
        'lat': p.latitud,
        'lng': p.longitud,
        'popup': f"<b>{p.nombres} {p.apellidos}</b><br>{p.direccion}"
      }
      for p in doctores
    ]

    context.update({
      'doctores_locations': doctores_locations,
      'default_image_url': static('img/doctor_avatar.webp'),
      'current_image_url': doctor.foto.url if doctor.foto else static('img/doctor_avatar.webp'),
      'back_url': self.success_url
    })

    context['is_edit_mode'] = True  # Para habilitar edición en el calendario
    return context

  def form_valid(self, form):
    horario_data = form.cleaned_data.get('horario_atencion')
    try:
      if horario_data:
        json.loads(horario_data)
    except json.JSONDecodeError:
      messages.error(self.request, "Error en el formato del horario de atención")
      return self.form_invalid(form)

    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar al Doctor {objAudit.nombre_completo}.")
    return response


class DoctorDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = Doctor
  permission_required = 'delete_doctor'
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Doctor'
    context['description'] = f"¿Desea Eliminar al Doctor: {self.object.nombre_completo}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente al Doctor {self.object.nombre_completo}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class DoctorDetailView(DetailView):
  model = Doctor
  extra_context = {
    "detail": "Detalles del Doctor"
  }

  def get(self, request, *args, **kwargs):
    doctor = self.get_object()
    data = {
      'id': doctor.id,
      'doctor': doctor.nombre_completo,
      'cedula': doctor.cedula,
      'fecha_nacimiento': doctor.fecha_nacimiento.isoformat() if doctor.fecha_nacimiento else None,
      'edad': doctor.calcular_edad(doctor.fecha_nacimiento),
      'direccion': doctor.direccion,
      'latitud': str(doctor.latitud) if doctor.latitud is not None else None,
      'longitud': str(doctor.longitud) if doctor.longitud is not None else None,
      'codigoUnicoDoctor': doctor.codigoUnicoDoctor,
      'especialidad': [especialidad.nombre for especialidad in doctor.especialidad.all()],
      'telefonos': doctor.telefonos,
      'email': doctor.email,
      'duracion_cita': doctor.duracion_cita,
      'curriculum': doctor.curriculum.url if doctor.curriculum else None,
      'firmaDigital': doctor.firmaDigital.url if doctor.firmaDigital else None,
      'foto': doctor.get_image(),
      'imagen_receta': doctor.imagen_receta.url if doctor.imagen_receta else None,
      'activo': doctor.activo,
    }
    return JsonResponse(data)


class DoctorHorarioDetailView(LoginRequiredMixin, UpdateView):
  model = Doctor
  template_name = 'core/doctor/horario.html'
  form_class = DoctorForm
  success_url = reverse_lazy('core:doctor_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['title1'] = 'Calendario del Doctor'
    context['doctor'] = f'Calendario del Doctor {self.object.nombre_completo}'
    # context['default_image_url'] = static('img/doctor_avatar.webp')
    context['current_image_url'] = self.object.foto.url if self.object.foto else static('img/doctor_avatar.webp')
    context['back_url'] = self.success_url
    context['is_edit_mode'] = True
    return context

  def form_valid(self, form):
    horario_data = form.cleaned_data.get('horario_atencion')
    try:
      if horario_data:
        json.loads(horario_data)
    except json.JSONDecodeError:
      messages.error(self.request, "Error en el formato del horario de atención")
      return self.form_invalid(form)

    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar al Doctor {objAudit.nombre_completo}.")
    return response
