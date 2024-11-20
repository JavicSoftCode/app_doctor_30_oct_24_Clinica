from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, ListView

from aplication.attention.models import *


class CostosAtencionListView(ListView):
  model = CostosAtencion
  template_name = "attention/costoAtencion/list.html"
  context_object_name = "costos"
  paginate_by = 5

  def get_queryset(self):
    # Filtrar por búsquedas si se envía un término por GET
    query = self.request.GET.get("q")
    queryset = CostosAtencion.objects.all().select_related("atencion")
    if query:
      queryset = queryset.filter(
        Q(atencion__paciente__nombre__icontains=query) |
        Q(atencion__paciente__dni__icontains=query)
      )
    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    costos = context['costos']  # Acceder a la lista de costos

    # Agregar información del paciente en el contexto
    for costo in costos:
      costo.paciente_nombre = costo.atencion.paciente.nombre_completo

    context['total'] = CostosAtencion.total
    return context


# class PagarCostoAtencionView(UpdateView):
#   model = CostosAtencion
#   template_name = "attention/costoAtencion/form.html"
#   success_url = reverse_lazy('attention:costos_atencion_list')
#   fields = []  # No direct editing
#
#   def get_object(self):
#     atencion_id = self.kwargs.get("pk")
#     atencion = get_object_or_404(Atencion, pk=atencion_id)
#     costos = CostosAtencion.objects.filter(atencion=atencion).first()
#     if not costos:
#       # Si no existe, lo creamos
#       costos = CostosAtencion.objects.create(
#         atencion=atencion,
#         total=0.00,
#         activo=False,
#       )
#     return costos
#
#   def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#
#     atencion = self.object.atencion
#
#     # Recalcular costos
#     detalles_medicamentos = [
#       {
#         'nombre': detalle.medicamento.nombre,
#         'cantidad': detalle.cantidad,
#         'precio_unitario': detalle.medicamento.precio,
#         'total': detalle.cantidad * detalle.medicamento.precio,
#       }
#       for detalle in atencion.atenciones.select_related('medicamento').all()
#     ]
#
#     detalles_servicios = [
#       {
#         'nombre_servicio': servicio.nombre_servicio,
#         'costo_servicio': servicio.costo_servicio,
#       }
#       for servicio in atencion.servicios_adicionales.all()
#     ]
#
#     subtotal_medicamentos = sum(detalle['total'] for detalle in detalles_medicamentos)
#     subtotal_servicios = sum(servicio['costo_servicio'] for servicio in detalles_servicios)
#     costo_base = 20  # Costo base de consulta
#     nuevo_total = subtotal_medicamentos + subtotal_servicios + costo_base
#
#     # Calcular diferencia con el total actual
#     total_anterior = self.object.total
#     diferencia = nuevo_total - total_anterior
#
#     mensaje_diferencia = "No se requiere ajuste en el pago."
#     if diferencia > 0:
#       mensaje_diferencia = f"Se requiere un cobro adicional de ${diferencia:.2f}."
#     elif diferencia < 0:
#       mensaje_diferencia = f"Se debe realizar un reembolso de ${abs(diferencia):.2f}."
#
#     # Actualizar contexto
#     context.update({
#       'paciente_nombre': atencion.paciente.nombre_completo,
#       'paciente_dni': atencion.paciente.cedula,
#       'detalles_medicamentos': detalles_medicamentos,
#       'detalles_servicios': detalles_servicios,
#       'subtotal_medicamentos': subtotal_medicamentos,
#       'subtotal_servicios': subtotal_servicios,
#       'monto_total': nuevo_total,
#       'diferencia': diferencia,
#       'mensaje_diferencia': mensaje_diferencia,
#       'pagado': self.object.activo,
#     })
#     return context
#
#   def post(self, request, *args, **kwargs):
#     costos = self.get_object()
#     atencion = costos.atencion
#
#     # Calcular nuevo total
#     subtotal_medicamentos = sum(
#       detalle.cantidad * detalle.medicamento.precio
#       for detalle in atencion.atenciones.select_related('medicamento').all()
#     )
#     subtotal_servicios = sum(
#       servicio.costo_servicio for servicio in atencion.servicios_adicionales.all()
#     )
#     costo_base = 20
#     nuevo_total = subtotal_medicamentos + subtotal_servicios + costo_base
#
#     diferencia = nuevo_total - costos.total
#     print(diferencia)
#     if not costos.activo:
#       costos.total = nuevo_total
#       costos.activo = True
#       costos.save()
#
#       if diferencia > 0:
#         messages.warning(request, f"Cobro adicional requerido: ${diferencia:.2f}")
#       elif diferencia < 0:
#         messages.info(request, f"Reembolso pendiente: ${abs(diferencia):.2f}")
#       else:
#         messages.success(request, "No se requieren ajustes en el pago.")
#
#       messages.success(request, "Pago procesado exitosamente.")
#     else:
#       messages.warning(request, "Este costo ya fue pagado.")
#
#     return redirect(reverse("attention:costos_atencion_list"))

class PagarCostoAtencionView(UpdateView):
    model = CostosAtencion
    template_name = "attention/costoAtencion/form.html"
    success_url = reverse_lazy('attention:costos_atencion_list')
    fields = []  # No direct editing

    def get_object(self):
      atencion_id = self.kwargs.get("pk")
      atencion = get_object_or_404(Atencion, pk=atencion_id)

      # Buscar o crear el costo asociado a la atención
      costos, created = CostosAtencion.objects.get_or_create(
        atencion=atencion,
        defaults={
          'total': self.calcular_total(atencion),
          'activo': False,
        }
      )
      if not created:
        # Recalcular y actualizar el total existente si no fue recién creado
        costos.total = self.calcular_total(atencion)
        costos.save()
      return costos

    def calcular_total(self, atencion):
      """
      Recalcula el costo total de la atención basada en medicamentos,
      servicios adicionales, y un costo base fijo.
      """
      subtotal_medicamentos = sum(
        detalle.cantidad * detalle.medicamento.precio
        for detalle in atencion.atenciones.select_related('medicamento').all()
      )
      subtotal_servicios = sum(
        servicio.costo_servicio for servicio in atencion.servicios_adicionales.all()
      )
      costo_base = 20  # Costo fijo de consulta
      return subtotal_medicamentos + subtotal_servicios + costo_base

    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      atencion = self.object.atencion

      # Recalcular costos y añadir al contexto
      detalles_medicamentos = [
        {
          'nombre': detalle.medicamento.nombre,
          'cantidad': detalle.cantidad,
          'precio_unitario': detalle.medicamento.precio,
          'total': detalle.cantidad * detalle.medicamento.precio,
        }
        for detalle in atencion.atenciones.select_related('medicamento').all()
      ]

      detalles_servicios = [
        {
          'nombre_servicio': servicio.nombre_servicio,
          'costo_servicio': servicio.costo_servicio,
        }
        for servicio in atencion.servicios_adicionales.all()
      ]

      subtotal_medicamentos = sum(detalle['total'] for detalle in detalles_medicamentos)
      subtotal_servicios = sum(servicio['costo_servicio'] for servicio in detalles_servicios)
      costo_base = 20
      nuevo_total = subtotal_medicamentos + subtotal_servicios + costo_base

      # Calcular diferencia con el total actual
      total_anterior = self.object.total
      diferencia = nuevo_total - total_anterior

      mensaje_diferencia = "No se requiere ajuste en el pago."
      if diferencia > 0:
        mensaje_diferencia = f"Se requiere un cobro adicional de ${diferencia:.2f}."
      elif diferencia < 0:
        mensaje_diferencia = f"Se debe realizar un reembolso de ${abs(diferencia):.2f}."

      context.update({
        'paciente_nombre': atencion.paciente.nombre_completo,
        'paciente_dni': atencion.paciente.cedula,
        'detalles_medicamentos': detalles_medicamentos,
        'detalles_servicios': detalles_servicios,
        'subtotal_medicamentos': subtotal_medicamentos,
        'subtotal_servicios': subtotal_servicios,
        'monto_total': nuevo_total,
        'diferencia': diferencia,
        'mensaje_diferencia': mensaje_diferencia,
        'pagado': self.object.activo,
      })
      return context

    def post(self, request, *args, **kwargs):
      costos = self.get_object()

      # Recalcular el total para asegurarnos de que esté actualizado
      nuevo_total = self.calcular_total(costos.atencion)
      diferencia = nuevo_total - costos.total

      if not costos.activo:
        costos.total = nuevo_total
        costos.activo = True
        costos.save()

        if diferencia > 0:
          messages.warning(request, f"Cobro adicional requerido: ${diferencia:.2f}")
        elif diferencia < 0:
          messages.info(request, f"Reembolso pendiente: ${abs(diferencia):.2f}")
        else:
          messages.success(request, "No se requieren ajustes en el pago.")

        messages.success(request, "Pago procesado exitosamente.")
      else:
        messages.warning(request, "Este costo ya fue pagado.")

      return redirect(self.success_url)
