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

from aplication.core.forms.empleado import EmpleadoForm
from aplication.core.models import Empleado
from aplication.security.mixins.mixins import *
from doctor.utils import save_audit


class EmpleadoListView(PermissionMixin, ListViewMixin, ListView):
  template_name = "core/empleado/list.html"
  model = Empleado
  permission_required = 'view_empleado'
  context_object_name = 'empleados'

  def get_queryset(self):
    self.query = Q()
    q1 = self.request.GET.get('q')  # ver
    empleado = self.request.GET.get('empleado')
    if q1 is not None:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)

      self.query.add(Q(nombres__icontains=q1), Q.OR)
      self.query.add(Q(apellidos__icontains=q1), Q.OR)
      self.query.add(Q(cedula__icontains=q1), Q.OR)
      self.query.add(Q(email__icontains=q1), Q.OR)
      if empleado in ["True", "False"]:
        is_active = empleado == "True"
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
        'image': location.foto.url if location.foto else static('img/avatar_empleado.png'),
      }
      for location in locations
      if location.latitud and location.longitud  # Solo incluir empleados con coordenadas válidas
    ]

    # Convertir a JSON de manera segura
    context['locations'] = json.dumps(locations_data, cls=DjangoJSONEncoder)
    return context


class EmpleadoCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = Empleado
  template_name = 'core/empleado/form.html'
  form_class = EmpleadoForm
  permission_required = 'add_empleado'
  success_url = reverse_lazy('core:empleado_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    # Mapa inicial centrado
    initial_map = folium.Map(location=[-2.129896, -79.593256], zoom_start=14)
    empleados = Empleado.objects.all()

    # Coordenadas de empleados existentes
    latitudes = [empleado.latitud for empleado in empleados]
    longitudes = [empleado.longitud for empleado in empleados]
    popups = [f"<b>{empleado.nombres} {empleado.apellidos}</b><br>{empleado.direccion}" for empleado in empleados]

    FastMarkerCluster(data=list(zip(latitudes, longitudes, popups))).add_to(initial_map)

    for empleado in empleados:
      folium.Marker(
        location=[empleado.latitud, empleado.longitud],
        popup=f"<b>{empleado.nombres} {empleado.apellidos}</b><br>{empleado.direccion}",
        icon=folium.Icon(icon='user', prefix='fa')
      ).add_to(initial_map)

    context['map'] = initial_map._repr_html_()
    context['default_image_url'] = static('img/avatar_empleado.png')
    # context['back_url'] = self.success_url
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='A')
    messages.success(self.request, f"Éxito al Crear al Empleado {objAudit.nombre_completo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al enviar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class EmpleadoUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = Empleado
  template_name = 'core/empleado/form.html'
  form_class = EmpleadoForm
  permission_required = 'change_empleado'
  success_url = reverse_lazy('core:empleado_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    empleado = self.object
    empleados = Empleado.objects.exclude(id=empleado.id)  # Excluir empleado actual

    # Preparar datos de ubicación de otros empleados
    empleados_locations = [
      {
        'lat': p.latitud,
        'lng': p.longitud,
        'popup': f"<b>{p.nombres} {p.apellidos}</b><br>{p.direccion}"
      }
      for p in empleados
    ]

    context.update({
      'empleados_locations': empleados_locations,
      'default_image_url': static('img/avatar_empleado.png'),
      'current_image_url': empleado.foto.url if empleado.foto else static('img/avatar_empleado.png'),
    })
    return context

  def form_valid(self, form):
    response = super().form_valid(form)
    objAudit = self.object
    save_audit(self.request, objAudit, action='M')
    messages.success(self.request, f"Éxito al Modificar al Empleado {objAudit.nombre_completo}.")
    return response

  def form_invalid(self, form):
    messages.error(self.request, "Error al Modificar el formulario. Corrige los errores.")
    print(form.errors)
    return self.render_to_response(self.get_context_data(form=form))


class EmpleadoDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = Empleado
  permission_required = 'delete_empleado'
  success_url = reverse_lazy('core:empleado_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['grabar'] = 'Eliminar Empleado'
    context['description'] = f"¿Desea Eliminar al Empleado: {self.object.nombre_completo}?"
    return context

  def delete(self, request, *args, **kwargs):
    self.object = self.get_object()
    success_message = f"Éxito al eliminar lógicamente al Empleado {self.object.nombre_completo}."
    messages.success(self.request, success_message)
    return super().delete(request, *args, **kwargs)


class EmpleadoDetailView(LoginRequiredMixin, DetailView):
  model = Empleado
  extra_context = {
    "detail": "Detalles del Empleado"
  }

  def get(self, request, *args, **kwargs):
    empleado = self.get_object()
    data = {
      'id': empleado.id,
      'empleado': empleado.nombre_completo,
      'cedula': empleado.cedula,
      'fecha_nacimiento': empleado.fecha_nacimiento.isoformat() if empleado.fecha_nacimiento else None,
      'edad': empleado.calcular_edad(empleado.fecha_nacimiento),
      'direccion': empleado.direccion,
      'latitud': str(empleado.latitud) if empleado.latitud is not None else None,
      'longitud': str(empleado.longitud) if empleado.longitud is not None else None,
      'cargo': empleado.cargo.nombre,
      'sueldo': empleado.sueldo,
      'telefonos': empleado.telefonos,
      'email': empleado.email,
      'curriculum': empleado.curriculum.url if empleado.curriculum else None,
      'firma_digital': empleado.firma_digital.url if empleado.firma_digital else None,
      'foto': empleado.get_image(),
      'activo': empleado.activo,
    }
    return JsonResponse(data)
