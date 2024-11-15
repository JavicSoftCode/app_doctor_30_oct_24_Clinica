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

from aplication.core.forms.patient import PatientForm
from aplication.core.models import Paciente
from doctor.mixins import CreateViewMixin, DeleteViewMixin, ListViewMixin, UpdateViewMixin
from doctor.utils import save_audit


class PatientListView(LoginRequiredMixin, ListViewMixin, ListView):
  template_name = "core/patient/list.html"
  model = Paciente
  context_object_name = 'pacientes'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')
    sex = self.request.GET.get('sex')
    if q1 is not None:
      self.query.add(Q(nombres__icontains=q1), Q.OR)
      self.query.add(Q(apellidos__icontains=q1), Q.OR)
      self.query.add(Q(cedula__icontains=q1), Q.OR)
    if sex == "M" or sex == "F":
      self.query.add(Q(sexo__icontains=sex), Q.AND)
    return self.model.objects.filter(self.query).order_by('apellidos')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    locations = self.get_queryset()
    locations_data = [
      {
        'latitude': float(location.latitud) if location.latitud else None,
        'longitude': float(location.longitud) if location.longitud else None,
        'paciente': location.nombre_completo,
        'address': location.direccion,
        'image': location.foto.url if location.foto else static('img/paciente_avatar.png'),
      }
      for location in locations
      if location.latitud and location.longitud  # Solo incluir pacientes con coordenadas válidas
    ]

    # Convertir a JSON de manera segura
    context['locations'] = json.dumps(locations_data, cls=DjangoJSONEncoder)
    return context


class PatientCreateView(LoginRequiredMixin, CreateViewMixin, CreateView):
  model = Paciente
  template_name = 'core/patient/form.html'
  form_class = PatientForm
  success_url = reverse_lazy('core:patient_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    # Mapa inicial centrado
    initial_map = folium.Map(location=[-2.129896, -79.593256], zoom_start=14)
    pacientes = Paciente.objects.all()
    # Coordenadas de pacientes existentes
    latitudes = [paciente.latitud for paciente in pacientes]
    longitudes = [paciente.longitud for paciente in pacientes]
    popups = [f"<b>{paciente.nombres} {paciente.apellidos}</b><br>{paciente.direccion}" for paciente in pacientes]

    FastMarkerCluster(data=list(zip(latitudes, longitudes, popups))).add_to(initial_map)

    for paciente in pacientes:
      folium.Marker(
        location=[paciente.latitud, paciente.longitud],
        popup=f"<b>{paciente.nombres} {paciente.apellidos}</b><br>{paciente.direccion}",
        icon=folium.Icon(icon='user', prefix='fa')
      ).add_to(initial_map)

    context['map'] = initial_map._repr_html_()
    context['default_image_url'] = static('img/paciente_avatar.png')
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    patient = self.object
    save_audit(self.request, patient, action='A')
    messages.success(self.request, f"Éxito al Crear el paciente {patient.nombre_completo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Crear el formulario. Corrige los errores.")
    return self.render_to_response(self.get_context_data(form=form))


class PatientUpdateView(LoginRequiredMixin, UpdateViewMixin, UpdateView):
  model = Paciente
  template_name = 'core/patient/form.html'
  form_class = PatientForm
  success_url = reverse_lazy('core:patient_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    patient = self.object
    patients = Paciente.objects.exclude(id=patient.id)  # Excluir paciente actual
    # Preparar datos de ubicación de otros pacientes
    patients_locations = [
      {
        'lat': p.latitud,
        'lng': p.longitud,
        'popup': f"<b>{p.nombres} {p.apellidos}</b><br>{p.direccion}"
      }
      for p in patients
    ]
    context.update({
      'patients_locations': patients_locations,
      'default_image_url': static('img/paciente_avatar.png'),
      'current_image_url': patient.foto.url if patient.foto else static('img/paciente_avatar.png'),
    })
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    patient = self.object
    save_audit(self.request, patient, action='M')
    messages.success(self.request, f"Éxito al Modificar el paciente {patient.nombre_completo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    return self.render_to_response(self.get_context_data(form=form))


class PatientDeleteView(LoginRequiredMixin, DeleteViewMixin, DeleteView):
  model = Paciente
  success_url = reverse_lazy('core:patient_list')

  # permission_required = 'delete_supplier'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['grabar'] = 'Eliminar paciente'
    context['description'] = f"¿Desea eliminar al paciente: {self.object.nombre_completo}?"
    context['back_url'] = self.success_url
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    # Verifica si el paciente tiene relaciones en `doctores_atencion` o `pacientes_examenes`
    if self.object.tiene_relaciones:
      messages.error(self.request,
                     "No se puede eliminar el paciente porque tiene atención médica o exámenes solicitados.")
      return redirect(self.success_url)

    success_message = f"Éxito al eliminar lógicamente al paciente {self.object.nombre_completo}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class PatientDetailView(LoginRequiredMixin, DetailView):
  model = Paciente

  def get(self, request, *args, **kwargs):
    try:
      pacient = self.get_object()
      data = {
        'id': pacient.id,
        'paciente': pacient.nombre_completo,
        'foto': pacient.get_image(),
        'fecha_nacimiento': pacient.fecha_nacimiento,
        'edad': pacient.calcular_edad(pacient.fecha_nacimiento),
        'cedula': pacient.cedula,
        'telefono': pacient.telefono,
        'email': pacient.email,
        'sexo': pacient.get_sexo_display() if pacient.sexo else None,
        'estado_civil': pacient.get_estado_civil_display() if pacient.estado_civil else None,
        'direccion': pacient.direccion,
        'latitud': pacient.latitud,
        'longitud': pacient.longitud,
        'tipo_sangre': pacient.tipo_sangre.tipo if pacient.tipo_sangre else None,
        'alergias': pacient.alergias,
        'enfermedades_cronicas': pacient.enfermedades_cronicas,
        'medicacion_actual': pacient.medicacion_actual,
        'cirugias_previas': pacient.cirugias_previas,
        'antecedentes_personales': pacient.antecedentes_personales,
        'antecedentes_familiares': pacient.antecedentes_familiares,
        'activo': pacient.activo,
      }
      return JsonResponse(data)
    except Paciente.DoesNotExist:
      raise Http404("Paciente no encontrado")
