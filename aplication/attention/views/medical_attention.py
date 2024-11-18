import json
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.platypus import SimpleDocTemplate

from aplication.attention.forms.medical_attention import AttentionForm
from aplication.attention.models import Atencion, DetalleAtencion
from aplication.core.models import Diagnostico, Medicamento
from aplication.security.mixins.mixins import *
from doctor.utils import custom_serializer, save_audit


def generar_factura(request, atencion_id):
  """Genera los detalles de la factura para una atención médica."""
  atencion = get_object_or_404(Atencion, id=atencion_id)

  # Detalles de medicamentos (incluyendo el total por medicamento)
  detalles_medicamentos = [
    {
      'nombre': detalle.medicamento.nombre,
      'cantidad': detalle.cantidad,
      'precio_unitario': detalle.medicamento.precio,
      'total': detalle.cantidad * detalle.medicamento.precio,
    }
    for detalle in atencion.atenciones.select_related('medicamento').all()
  ]

  # Detalles de servicios adicionales
  detalles_servicios = [
    {
      'nombre_servicio': servicio.nombre_servicio,
      'costo_servicio': servicio.costo_servicio,
    }
    for servicio in atencion.servicios_adicionales.select_related().all()
  ]

  # Cálculo de subtotales
  subtotal_medicamentos = sum(detalle['total'] for detalle in detalles_medicamentos)
  subtotal_servicios = sum(servicio['costo_servicio'] for servicio in detalles_servicios)

  # Cálculo del monto total
  monto_total = subtotal_medicamentos + subtotal_servicios

  return render(request, 'attention/medical_attention/factura.html', {
    'factura': {
      'atencion': atencion,
      'monto_total': monto_total,
    },
    'detalles_medicamentos': detalles_medicamentos,
    'detalles_servicios': detalles_servicios,
    'subtotal_medicamentos': subtotal_medicamentos,
    'subtotal_servicios': subtotal_servicios,
  })



@login_required
def generar_certificado_pdf(request, pk):
  # Obtener la atención médica
  # atencion = get_object_or_404(Atencion)
  atencion = get_object_or_404(Atencion, pk=pk)
  # Crear la respuesta HTTP con tipo de contenido PDF
  response = HttpResponse(content_type='application/pdf')
  sanitized_name = atencion.paciente.nombre_completo.replace(" ", "_")
  response[
    'Content-Disposition'] = f'attachment; filename="certificado_medico_{sanitized_name}_{atencion.fecha_atencion.date()}.pdf"'

  # Crear el documento PDF
  doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
  elements = []
  styles = getSampleStyleSheet()

  # Estilo personalizado para el título
  styles.add(ParagraphStyle(
    name='CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#3498db'),
    alignment=TA_CENTER,
    spaceAfter=20
  ))

  # Título del certificado
  elements.append(Paragraph('CERTIFICADO MÉDICO', styles['CustomTitle']))
  elements.append(Spacer(1, 12))

  # Encabezado con información del paciente
  elements.append(Paragraph(f"Paciente: {atencion.paciente.nombre_completo}", styles['Normal']))
  elements.append(Paragraph(f"Cédula: {atencion.paciente.cedula}", styles['Normal']))
  elements.append(Paragraph(f"Fecha de Atención: {atencion.fecha_atencion.strftime('%d/%m/%Y')}", styles['Normal']))
  elements.append(Spacer(1, 12))

  # Signos vitales
  elements.append(Paragraph("Signos Vitales", styles['Heading2']))
  signos_vitales = [
    ['Presión Arterial', atencion.presion_arterial or 'No especificado'],
    ['Pulso', f"{atencion.pulso} ppm" if atencion.pulso else 'No especificado'],
    ['Temperatura', f"{atencion.temperatura} °C" if atencion.temperatura else 'No especificado'],
    ['Frecuencia Respiratoria',
     f"{atencion.frecuencia_respiratoria} rpm" if atencion.frecuencia_respiratoria else 'No especificado'],
    ['Saturación de Oxígeno', f"{atencion.saturacion_oxigeno}%" if atencion.saturacion_oxigeno else 'No especificado'],
    ['Peso', f"{atencion.peso} kg" if atencion.peso else 'No especificado'],
    ['Altura', f"{atencion.altura} m" if atencion.altura else 'No especificado'],
  ]
  signos_table = Table(signos_vitales, colWidths=[3 * inch, 3 * inch])
  signos_table.setStyle(TableStyle([
    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f8ff')),
  ]))
  elements.append(signos_table)
  elements.append(Spacer(1, 12))

  # Diagnóstico y tratamiento
  elements.append(Paragraph("Diagnóstico y Tratamiento", styles['Heading2']))
  elements.append(Paragraph(f"Diagnóstico: {atencion.get_diagnosticos or 'No especificado'}", styles['Normal']))
  elements.append(Paragraph(f"Motivo de Consulta: {atencion.motivo_consulta}", styles['Normal']))
  elements.append(Paragraph(f"Síntomas: {atencion.sintomas}", styles['Normal']))
  elements.append(Paragraph(f"Tratamiento: {atencion.tratamiento}", styles['Normal']))
  elements.append(Spacer(1, 12))

  # Medicamentos recetados
  elements.append(Paragraph("Medicamentos Recetados", styles['Heading2']))
  detalles = DetalleAtencion.objects.filter(atencion=atencion)
  if detalles.exists():
    medicamentos_data = [['Medicamento', 'Cantidad', 'Prescripción']]
    for detalle in detalles:
      medicamentos_data.append([
        detalle.medicamento.nombre,
        detalle.cantidad,
        detalle.prescripcion or 'No especificado'
      ])
    medicamentos_table = Table(medicamentos_data, colWidths=[2.5 * inch, 1.5 * inch, 3 * inch])
    medicamentos_table.setStyle(TableStyle([
      ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2ecc71')),
      ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
      ('FONTSIZE', (0, 0), (-1, -1), 10),
      ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
      ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f6f3')),
    ]))
    elements.append(medicamentos_table)
  else:
    elements.append(Paragraph("No se recetaron medicamentos en esta atención.", styles['Normal']))

  # Generar el PDF
  doc.title = f"Certificado Médico - {atencion.paciente.nombre_completo}"
  doc.build(elements)
  return response


class ViewAtencionPdf(LoginRequiredMixin, View):
  def get(self, request, *args, **kwargs):
    try:
      # Obtener la atención médica usando el pk de la URL
      atencion = Atencion.objects.prefetch_related('diagnostico', 'atenciones').get(pk=kwargs['pk'])

      # Obtener los detalles de la atención (medicamentos recetados)
      detalles = DetalleAtencion.objects.filter(atencion=atencion)

      # Preparar los datos en un diccionario
      data = {
        'id': atencion.id,
        'title1': f' Atención {atencion.id}',
        'paciente': atencion.paciente.nombre_completo,
        'fecha_atencion': atencion.fecha_atencion,
        'edad': atencion.paciente.calcular_edad(atencion.paciente.fecha_nacimiento),
        'sexo': atencion.paciente.get_sexo_display() if atencion.paciente.sexo else None,
        'presion_arterial': atencion.presion_arterial,
        'pulso': atencion.pulso,
        'temperatura': atencion.temperatura,
        'frecuencia_respiratoria': atencion.frecuencia_respiratoria,
        'saturacion_oxigeno': atencion.saturacion_oxigeno,
        'peso': atencion.peso,
        'altura': atencion.altura,
        'motivo_consulta': atencion.motivo_consulta,
        'sintomas': atencion.sintomas,
        'tratamiento': atencion.tratamiento,
        'diagnosticos': atencion.get_diagnosticos,
        'examen_fisico': atencion.examen_fisico,
        'examenes_enviados': atencion.examenes_enviados,
        'comentario_adicional': atencion.comentario_adicional,
        'imc': atencion.calcular_imc,
        'detalles': detalles,  # Detalles de los medicamentos recetados
      }

      # Aquí se puede renderizar un PDF o generar la ficha médica
      return render(request, 'attention/medical_attention/atencion_pdf.html', data)
    except Atencion.DoesNotExist:
      raise Http404("No se encontró la atención médica.")


class AttentionListView(PermissionMixin, ListViewMixin, ListView):
  template_name = "attention/medical_attention/list.html"
  model = Atencion
  permission_required = 'view_attention'
  context_object_name = 'atenciones'

  def get_queryset(self):
    # self.query = Q()
    q1 = self.request.GET.get('q')  # ver
    sex = self.request.GET.get('sex')
    if q1 is not None:
      self.query.add(Q(paciente__nombres__icontains=q1), Q.OR)
      self.query.add(Q(paciente__apellidos__icontains=q1), Q.OR)
      self.query.add(Q(paciente__cedula__icontains=q1), Q.OR)
    if sex == "M" or sex == "F": self.query.add(Q(paciente__sexo__icontains=sex), Q.AND)
    return self.model.objects.filter(self.query).order_by('-fecha_atencion')


class AttentionCreateView(PermissionMixin, CreateViewMixin, CreateView):
  model = Atencion
  template_name = 'attention/medical_attention/form.html'
  form_class = AttentionForm
  permission_required = 'add_attention'
  success_url = reverse_lazy('attention:attention_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    context['detail_atencion'] = []
    context["medications"] = Medicamento.objects.filter(activo=True).order_by('nombre')
    return context

  def post(self, request, *args, **kwargs):
    data = json.loads(request.body)
    medicamentos = data['medicamentos']
    try:
      with transaction.atomic():
        # Crear la instancia de Atencion
        atencion = Atencion.objects.create(
          paciente_id=int(data['paciente']),
          presion_arterial=data['presionArterial'],
          pulso=int(data['pulso']),
          temperatura=Decimal(data['temperatura']),
          frecuencia_respiratoria=int(data['frecuenciaRespiratoria']),
          saturacion_oxigeno=Decimal(data['saturacionOxigeno']),
          peso=Decimal(data['peso']),
          altura=Decimal(data['altura']),
          motivo_consulta=data['motivoConsulta'],
          sintomas=data['sintomas'],
          tratamiento=data['tratamiento'],
          examen_fisico=data['examenFisico'],
          examenes_enviados=data['examenesEnviados'],
          comentario_adicional=data['comentarioAdicional'],
          fecha_atencion=timezone.now()
        )
        diagnostico_ids = data.get('diagnostico', [])
        diagnosticos = Diagnostico.objects.filter(id__in=diagnostico_ids)
        atencion.diagnostico.set(diagnosticos)
        atencion.save()

        for medicamento in medicamentos:
          DetalleAtencion.objects.create(
            atencion=atencion,
            medicamento_id=int(medicamento['codigo']),
            cantidad=int(medicamento['cantidad']),
            prescripcion=medicamento['prescripcion'],
          )

        # Generar y enviar el correo electrónico
        self.enviar_correo_con_pdf(atencion)

        save_audit(request, atencion, "A")
        messages.success(self.request, f"Éxito al registrar la atención médica #{atencion.id}")
        return JsonResponse({"msg": "Éxito al registrar la atención médica."}, status=200)
    except Exception as ex:
      messages.error(self.request, f"Error al registrar la atención médica")
      return JsonResponse({"msg": str(ex)}, status=400)

  def generar_pdf(self, atencion):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
      name='CustomTitle',
      parent=styles['Heading1'],
      fontSize=16,
      textColor=colors.HexColor('#3498db'),
      alignment=TA_CENTER,
      spaceAfter=20
    ))

    elements.append(Paragraph('CERTIFICADO MÉDICO', styles['CustomTitle']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Paciente: {atencion.paciente.nombre_completo}", styles['Normal']))
    elements.append(Paragraph(f"Cédula: {atencion.paciente.cedula}", styles['Normal']))
    elements.append(Paragraph(f"Fecha de Atención: {atencion.fecha_atencion.strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    signos_vitales = [
      ['Presión Arterial', atencion.presion_arterial or 'No especificado'],
      ['Pulso', f"{atencion.pulso} ppm" if atencion.pulso else 'No especificado'],
      ['Temperatura', f"{atencion.temperatura} °C" if atencion.temperatura else 'No especificado'],
      ['Frecuencia Respiratoria',
       f"{atencion.frecuencia_respiratoria} rpm" if atencion.frecuencia_respiratoria else 'No especificado'],
      ['Saturación de Oxígeno',
       f"{atencion.saturacion_oxigeno}%" if atencion.saturacion_oxigeno else 'No especificado'],
      ['Peso', f"{atencion.peso} kg" if atencion.peso else 'No especificado'],
      ['Altura', f"{atencion.altura} m" if atencion.altura else 'No especificado'],
    ]
    signos_table = Table(signos_vitales, colWidths=[3 * inch, 3 * inch])
    signos_table.setStyle(TableStyle([
      ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),
      ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
      ('FONTSIZE', (0, 0), (-1, -1), 10),
      ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(signos_table)
    elements.append(Spacer(1, 12))

    detalles = DetalleAtencion.objects.filter(atencion=atencion)
    if detalles.exists():
      medicamentos_data = [['Medicamento', 'Cantidad', 'Prescripción']]
      for detalle in detalles:
        medicamentos_data.append([
          detalle.medicamento.nombre,
          detalle.cantidad,
          detalle.prescripcion or 'No especificado'
        ])
      medicamentos_table = Table(medicamentos_data, colWidths=[2.5 * inch, 1.5 * inch, 3 * inch])
      medicamentos_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2ecc71')),
      ]))
      elements.append(medicamentos_table)
    else:
      elements.append(Paragraph("No se recetaron medicamentos.", styles['Normal']))

    doc.title = f"Certificado Médico - {atencion.paciente.nombre_completo}"
    doc.build(elements)
    buffer.seek(0)
    return buffer

  def enviar_correo_con_pdf(self, atencion):
    pdf_buffer = self.generar_pdf(atencion)
    paciente_email = atencion.paciente.email
    email = EmailMessage(
      subject='Certificado Médico',
      body=f"Estimado/a {atencion.paciente.nombre_completo}, adjuntamos su certificado médico.",
      from_email='ing.javiersistem02ejqp@gmail.com',
      to=[paciente_email],
    )
    email.attach(f"certificado_medico_{atencion.paciente.nombre_completo}.pdf", pdf_buffer.read(), 'application/pdf')
    email.send()


class AttentionUpdateView(PermissionMixin, UpdateViewMixin, UpdateView):
  model = Atencion
  template_name = 'attention/medical_attention/form.html'
  form_class = AttentionForm
  permission_required = 'change_attention'
  success_url = reverse_lazy('attention:attention_list')

  # permission_required = 'add_supplier' # en PermissionMixn se verfica si un grupo tiene el permiso

  def get_context_data(self, **kwargs):
    context = super().get_context_data()
    # Obtiene una lista de medicamentos activos usando un método del modelo Medicamento.
    # Extrae solo los campos 'id' y 'nombre', y los ordena alfabéticamente por 'nombre'
    context["medications"] = Medicamento.objects.filter(activo=True).order_by('nombre')

    # context["medications"] = Medicamento.active_medication.values('id', 'nombre').order_by('nombre')
    # Obtiene una lista de detalles de atención relacionados con la atención actual (self.object.id)
    # Filtra por el ID de la atención y selecciona los campos 'medicamento_id', 'medicamento_nombre',
    # 'cantidad' y 'prescripcion' para optimizar la consulta
    detail_atencion = list(
      DetalleAtencion.objects.filter(atencion_id=self.object.id).values("medicamento_id", "medicamento__nombre",
                                                                        "cantidad", "prescripcion"))
    # Convierte la lista de diccionarios en una cadena JSON para que pueda ser usada en JavaScript.
    # Utiliza un serializador personalizado 'custom_serializer' para manejar tipos de datos especiales
    detail_atencion = json.dumps(detail_atencion, default=custom_serializer)
    # Agrega los detalles de la atención al contexto con la clave 'detail_atencion'
    # El resultado será un string JSON como: '[{"id": 1, "nombre": "aspirina"}, {...}, {...}]'
    context['detail_atencion'] = detail_atencion
    return context

  def post(self, request, *args, **kwargs):
    # Convertir el cuerpo de la solicitud a un diccionario Python
    data = json.loads(request.body)
    print(data)
    medicamentos = data['medicamentos']
    print(medicamentos)
    try:
      atencion = Atencion.objects.get(id=self.kwargs.get('pk'))
      print(atencion)
      with transaction.atomic():
        # Crear la instancia del modelo Atencion
        atencion.paciente_id = int(data['paciente'])
        atencion.presion_arterial = data['presionArterial']
        atencion.pulso = int(data['pulso'])
        atencion.temperatura = Decimal(data['temperatura'])
        atencion.frecuencia_respiratoria = int(data['frecuenciaRespiratoria'])
        atencion.saturacion_oxigeno = Decimal(data['saturacionOxigeno'])
        atencion.peso = Decimal(data['peso'])
        atencion.altura = Decimal(data['altura'])
        atencion.motivo_consulta = data['motivoConsulta']
        atencion.sintomas = data['sintomas']
        atencion.tratamiento = data['tratamiento']
        atencion.examen_fisico = data['examenFisico']
        atencion.examenes_enviados = data['examenesEnviados']
        atencion.comentario_adicional = data['comentarioAdicional']
        print("datos de diagnostico")
        diagnostico_ids = data.get('diagnostico', [])
        print("diag=", diagnostico_ids)
        diagnosticos = Diagnostico.objects.filter(id__in=diagnostico_ids)
        atencion.diagnostico.set(diagnosticos)
        atencion.save()
        print("grabo atencion")
        # borrar el detalle asociado a esa atencion
        DetalleAtencion.objects.filter(atencion_id=atencion.id).delete()
        # Ahora procesamos el arreglo de medicamentos
        print("voy a medicamentos update")
        for medicamento in medicamentos:
          # Crear el detalle de atención para cada medicamento
          DetalleAtencion.objects.create(
            atencion=atencion,
            medicamento_id=int(medicamento['codigo']),
            cantidad=int(medicamento['cantidad']),
            prescripcion=medicamento['prescripcion'],
            # Si necesitas la duración del tratamiento, puedes agregarla aquí
          )

        # Generar y enviar el correo electrónico
        self.enviar_correo_con_pdf(atencion)

        save_audit(request, atencion, "M")
        messages.success(self.request, f"Éxito al Actualizar la atención médica #{atencion.id}")
        return JsonResponse({"msg": "Éxito al Actualizar la atención médica."}, status=200)
    except Exception as ex:
      messages.error(self.request, f"Érro al actualizar la atención médica")
      return JsonResponse({"msg": str(ex)}, status=400)

  def generar_pdf(self, atencion):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
      name='CustomTitle',
      parent=styles['Heading1'],
      fontSize=16,
      textColor=colors.HexColor('#3498db'),
      alignment=TA_CENTER,
      spaceAfter=20
    ))

    elements.append(Paragraph('CERTIFICADO MÉDICO ACTUALIZADO', styles['CustomTitle']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Paciente: {atencion.paciente.nombre_completo}", styles['Normal']))
    elements.append(Paragraph(f"Cédula: {atencion.paciente.cedula}", styles['Normal']))
    elements.append(Paragraph(f"Fecha de Atención: {atencion.fecha_atencion.strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    signos_vitales = [
      ['Presión Arterial', atencion.presion_arterial or 'No especificado'],
      ['Pulso', f"{atencion.pulso} ppm" if atencion.pulso else 'No especificado'],
      ['Temperatura', f"{atencion.temperatura} °C" if atencion.temperatura else 'No especificado'],
      ['Frecuencia Respiratoria',
       f"{atencion.frecuencia_respiratoria} rpm" if atencion.frecuencia_respiratoria else 'No especificado'],
      ['Saturación de Oxígeno',
       f"{atencion.saturacion_oxigeno}%" if atencion.saturacion_oxigeno else 'No especificado'],
      ['Peso', f"{atencion.peso} kg" if atencion.peso else 'No especificado'],
      ['Altura', f"{atencion.altura} m" if atencion.altura else 'No especificado'],
    ]
    signos_table = Table(signos_vitales, colWidths=[3 * inch, 3 * inch])
    signos_table.setStyle(TableStyle([
      ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),
      ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
      ('FONTSIZE', (0, 0), (-1, -1), 10),
      ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(signos_table)
    elements.append(Spacer(1, 12))

    detalles = DetalleAtencion.objects.filter(atencion=atencion)
    if detalles.exists():
      medicamentos_data = [['Medicamento', 'Cantidad', 'Prescripción']]
      for detalle in detalles:
        medicamentos_data.append([
          detalle.medicamento.nombre,
          detalle.cantidad,
          detalle.prescripcion or 'No especificado'
        ])
      medicamentos_table = Table(medicamentos_data, colWidths=[2.5 * inch, 1.5 * inch, 3 * inch])
      medicamentos_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2ecc71')),
      ]))
      elements.append(medicamentos_table)
    else:
      elements.append(Paragraph("No se recetaron medicamentos.", styles['Normal']))

    doc.title = f"Certificado Médico Actualizado - {atencion.paciente.nombre_completo}"
    doc.build(elements)
    buffer.seek(0)
    return buffer

  def enviar_correo_con_pdf(self, atencion):
    pdf_buffer = self.generar_pdf(atencion)
    paciente_email = atencion.paciente.email
    email = EmailMessage(
      subject='Certificado Médico Actualizado',
      body=f"Estimado/a su certificado medico a sido actualizado Sr. ( a ) {atencion.paciente.nombre_completo}, adjuntamos su certificado médico.",
      from_email='ing.javiersistem02ejqp@gmail.com',
      to=[paciente_email],
    )
    email.attach(f"certificado_actualizado_medico_{atencion.paciente.nombre_completo}.pdf", pdf_buffer.read(),
                 'application/pdf')
    email.send()


class AttentionDetailView(LoginRequiredMixin, DetailView):
  model = Atencion

  def get(self, request, *args, **kwargs):
    print("entro get")
    atencion = self.get_object()
    print(atencion)
    detail_atencion = list(
      DetalleAtencion.objects.filter(atencion_id=atencion.id).values("medicamento_id", "medicamento__nombre",
                                                                     "cantidad", "prescripcion"))
    detail_atencion = json.dumps(detail_atencion, default=custom_serializer)
    data = {
      'id': atencion.id,
      'nombres': atencion.paciente.nombre_completo,
      'foto': atencion.paciente.get_image(),
      'detalle_atencion': detail_atencion
    }
    print(data)
    return JsonResponse(data)
