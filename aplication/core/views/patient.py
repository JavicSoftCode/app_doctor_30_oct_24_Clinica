import json
from django.db.models import Prefetch
import folium
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from folium.plugins import FastMarkerCluster
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

from aplication.core.forms.patient import PatientForm
from aplication.core.models import Paciente
from aplication.attention.models import ExamenSolicitado
from aplication.security.mixins.mixins import *
from doctor.utils import save_audit


@login_required
def generar_ficha_pdf(request):
  # Obtener el paciente
  paciente = get_object_or_404(Paciente)

  # Crear la respuesta HTTP con el tipo de contenido PDF
  response = HttpResponse(content_type='application/pdf')
  sanitized_name = paciente.nombre_completo.replace(" ", "_")
  response['Content-Disposition'] = f'attachment; filename="ficha_medica_{sanitized_name}__c.i__{paciente.cedula}.pdf"'

  # Crear el documento PDF
  doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
  elements = []
  styles = getSampleStyleSheet()

  # Estilo personalizado para el título
  styles.add(ParagraphStyle(
    name='CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#9b59b6'),
    alignment=TA_CENTER,
    spaceAfter=20
  ))

  # Encabezado con título
  elements.append(Paragraph('FICHA MÉDICA<br/>COLEGIO PHIDIAS', styles['CustomTitle']))
  elements.append(Spacer(1, 12))
  elements.append(Paragraph(f'Fecha de Creación: {paciente.fecha_creacion.strftime("%d/%m/%Y")}', styles['Normal']))
  elements.append(Spacer(1, 12))

  # Foto del paciente
  if paciente.foto:
    elements.append(Image(paciente.foto.path, width=1.5 * inch, height=1.5 * inch))
  else:
    elements.append(Paragraph('Sin imagen disponible', styles['Normal']))
  elements.append(Spacer(1, 12))

  # Información básica
  elements.append(Paragraph('Información Básica', styles['Heading2']))
  basic_data = [
    ['Nombre Completo:', paciente.nombre_completo],
    ['Cédula:', paciente.cedula],
    ['Fecha de Nacimiento:', paciente.fecha_nacimiento.strftime('%d/%m/%Y')],
    ['Edad:', f'{paciente.calcular_edad(paciente.fecha_nacimiento)} años'],
    ['Teléfono:', paciente.telefono],
    ['Correo:', paciente.email or 'No especificado'],
    ['Sexo:', paciente.sexo],
    ['Estado Civil:', paciente.estado_civil],
    ['Dirección:', paciente.direccion]
  ]
  table_style = TableStyle([
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#9b59b6')),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
  ])
  basic_table = Table(basic_data, colWidths=[2.5 * inch, 4 * inch])
  basic_table.setStyle(table_style)
  elements.append(basic_table)
  elements.append(Spacer(1, 12))

  # Datos médicos
  elements.append(Paragraph('Información Médica', styles['Heading2']))
  medical_data = [
    ['Tipo de Sangre:', paciente.tipo_sangre.tipo if paciente.tipo_sangre else 'No especificado'],
    ['Alergias:', paciente.alergias or 'No especificado'],
    ['Enfermedades Crónicas:', paciente.enfermedades_cronicas or 'No especificado'],
    ['Medicación Actual:', paciente.medicacion_actual or 'No especificado'],
    ['Cirugías Previas:', paciente.cirugias_previas or 'No especificado']
  ]
  medical_table = Table(medical_data, colWidths=[2.5 * inch, 4 * inch])
  medical_table.setStyle(table_style)
  elements.append(medical_table)
  elements.append(Spacer(1, 12))

  # Antecedentes médicos
  elements.append(Paragraph('Antecedentes Médicos', styles['Heading2']))
  history_data = [
    ['Antecedentes Personales:', paciente.antecedentes_personales or 'No especificado'],
    ['Antecedentes Familiares:', paciente.antecedentes_familiares or 'No especificado']
  ]
  history_table = Table(history_data, colWidths=[2.5 * inch, 4 * inch])
  history_table.setStyle(table_style)
  elements.append(history_table)

  # Generar PDF
  doc.title = f"Ficha Médica - {paciente.nombre_completo}"
  doc.build(elements)
  return response


class ViewPatientPdf(LoginRequiredMixin, View):

  def get(self, request, *args, **kwargs):
    try:
      # Obtener el paciente usando el pk de la URL
      paciente = Paciente.objects.get(pk=kwargs['pk'])

      # Preparar los datos del paciente en un diccionario
      data = {
        'id': paciente.id,
        'paciente': paciente.nombre_completo,
        'title1': f' Ficha {paciente.id}',
        'foto': paciente.get_image(),  # Método para obtener la imagen
        'fecha_nacimiento': paciente.fecha_nacimiento,
        'edad': paciente.calcular_edad(paciente.fecha_nacimiento),  # Método para calcular la edad
        'cedula': paciente.cedula,
        'telefono': paciente.telefono,
        'email': paciente.email,
        'sexo': paciente.get_sexo_display() if paciente.sexo else None,
        'estado_civil': paciente.get_estado_civil_display() if paciente.estado_civil else None,
        'direccion': paciente.direccion,
        'latitud': paciente.latitud,
        'longitud': paciente.longitud,
        'tipo_sangre': paciente.tipo_sangre.tipo if paciente.tipo_sangre else None,
        'alergias': paciente.alergias,
        'enfermedades_cronicas': paciente.enfermedades_cronicas,
        'medicacion_actual': paciente.medicacion_actual,
        'cirugias_previas': paciente.cirugias_previas,
        'antecedentes_personales': paciente.antecedentes_personales,
        'antecedentes_familiares': paciente.antecedentes_familiares,
        'fecha_creacion': paciente.fecha_creacion,
        'activo': paciente.activo,
      }

      # Renderizar el HTML con los datos del paciente
      return render(request, 'core/patient/ficha_medica.html', data)

    except Paciente.DoesNotExist:
      # Si el paciente no existe, lanzar un error 404
      raise Http404("Paciente no encontrado")


# class PatientListView(PermissionMixin, ListViewMixin, ListView):
#   template_name = "core/patient/list.html"
#   model = Paciente
#   permission_required = 'view_paciente'
#   context_object_name = 'pacientes'
#
#   def get_queryset(self):
#     self.query = Q()
#     q1 = self.request.GET.get('q')
#     sex = self.request.GET.get('sex')
#     if q1 is not None:
#       self.query.add(Q(nombres__icontains=q1), Q.OR)
#       self.query.add(Q(apellidos__icontains=q1), Q.OR)
#       self.query.add(Q(cedula__icontains=q1), Q.OR)
#     if sex == "M" or sex == "F":
#       self.query.add(Q(sexo__icontains=sex), Q.AND)
#     return self.model.objects.filter(self.query).order_by('apellidos')
#
#   def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     locations = self.get_queryset()
#     locations_data = [
#       {
#         'latitude': float(location.latitud) if location.latitud else None,
#         'longitude': float(location.longitud) if location.longitud else None,
#         'paciente': location.nombre_completo,
#         'address': location.direccion,
#         'image': location.foto.url if location.foto else static('img/paciente_avatar.png'),
#       }
#       for location in locations
#       if location.latitud and location.longitud  # Solo incluir pacientes con coordenadas válidas
#     ]
#
#     # Convertir a JSON de manera segura
#     context['locations'] = json.dumps(locations_data, cls=DjangoJSONEncoder)
#     return context


# class PatientListView(PermissionMixin, ListViewMixin, ListView):
#   template_name = "core/patient/list.html"
#   model = Paciente
#   permission_required = 'view_paciente'
#   context_object_name = 'pacientes'
#
#   def get_queryset(self):
#     self.query = Q()
#     q1 = self.request.GET.get('q')
#     sex = self.request.GET.get('sex')
#     if q1 is not None:
#       self.query.add(Q(nombres__icontains=q1), Q.OR)
#       self.query.add(Q(apellidos__icontains=q1), Q.OR)
#       self.query.add(Q(cedula__icontains=q1), Q.OR)
#     if sex == "M" or sex == "F":
#       self.query.add(Q(sexo__icontains=sex), Q.AND)
#     return self.model.objects.filter(self.query).order_by('apellidos')
#
#   def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     locations = self.get_queryset()
#     locations_data = [
#       {
#         'latitude': float(location.latitud) if location.latitud else None,
#         'longitude': float(location.longitud) if location.longitud else None,
#         'paciente': location.nombre_completo,
#         'address': location.direccion,
#         'image': location.foto.url if location.foto else static('img/paciente_avatar.png'),
#         'examenes_realizados': [
#           {
#             'nombre_examen': examen.nombre_examen,
#             'fecha_solicitud': examen.fecha_solicitud.strftime('%Y-%m-%d'),
#             'resultado': examen.resultado.url if examen.resultado else None,
#           }
#           for examen in location.pacientes_examenes.filter(estado='R')
#         ],  # Convertir QuerySet a lista de diccionarios
#       }
#       for location in locations
#       if location.latitud and location.longitud  # Solo incluir pacientes con coordenadas válidas
#     ]
#
#     # Serializar la lista resultante
#     context['locations'] = json.dumps(locations_data, cls=DjangoJSONEncoder)
#     return context

class PatientListView(PermissionMixin, ListViewMixin, ListView):
    template_name = "core/patient/list.html"
    model = Paciente
    permission_required = 'view_paciente'
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
      # Prefetch exámenes realizados
      return (
        self.model.objects.filter(self.query)
        .prefetch_related(
          Prefetch(
            'pacientes_examenes',
            queryset=ExamenSolicitado.objects.filter(estado='R'),
            to_attr='examenes_realizados'
          )
        )
        .order_by('apellidos')
      )

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
          'examenes_realizados': [
            {
              'id': examen.id,
              'nombre_examen': examen.nombre_examen,
              'fecha_solicitud': examen.fecha_solicitud.strftime('%Y-%m-%d'),
              'resultado': examen.resultado.url if examen.resultado else None,
            }
            for examen in location.examenes_realizados  # Ya prefetch
          ],
        }
        for location in locations
        if location.latitud and location.longitud  # Solo incluir pacientes con coordenadas válidas
      ]

      context['locations'] = json.dumps(locations_data, cls=DjangoJSONEncoder)
      return context


class PatientCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = Paciente
  template_name = 'core/patient/form.html'
  form_class = PatientForm
  permission_required = 'add_paciente'
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


class PatientUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = Paciente
  template_name = 'core/patient/form.html'
  form_class = PatientForm
  permission_required = 'change_paciente'
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


class PatientDeleteView(PermissionMixin, DeleteViewMixin, DeleteView):
  model = Paciente
  permission_required = 'delete_paciente'
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
