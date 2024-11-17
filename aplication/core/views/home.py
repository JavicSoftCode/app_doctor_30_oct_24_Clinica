import calendar

from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timesince import timesince
from django.views.generic import TemplateView

from aplication.attention.models import CitaMedica, Atencion
from aplication.core.models import Paciente


# views.py

class HomeTemplateView(TemplateView):
  template_name = 'core/home.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    ahora = timezone.now().replace(tzinfo=None)

    # Obtener la última atención registrada
    ultima_atencion = Atencion.objects.order_by('-fecha_atencion').first()
    tiempo_desde_ultima_atencion = None
    if ultima_atencion:
      fecha_atencion_naive = ultima_atencion.fecha_atencion.replace(tzinfo=None)
      tiempo_desde_ultima_atencion = timesince(fecha_atencion_naive, ahora)

    # Obtener la última cita médica con estado "R" (Realizada)
    ultima_cita_realizada = CitaMedica.objects.filter(
      estado='R'
    ).order_by('-fecha_creacion').first()  # Usar `fecha_creacion` para calcular el tiempo exacto

    # Calcular el tiempo transcurrido desde la creación de la última cita realizada
    tiempo_desde_ultima_cita = None
    if ultima_cita_realizada:
      fecha_creacion_naive = ultima_cita_realizada.fecha_creacion.replace(tzinfo=None)
      tiempo_desde_ultima_cita = timesince(fecha_creacion_naive, ahora)

    # Obtener el último paciente registrado
    ultimo_paciente = Paciente.objects.order_by('-fecha_creacion').first()

    # Calcular el tiempo transcurrido desde el último paciente registrado
    tiempo_desde_ultimo_paciente = None
    if ultimo_paciente:
      fecha_creacion_naive = ultimo_paciente.fecha_creacion.replace(tzinfo=None)
      tiempo_desde_ultimo_paciente = timesince(fecha_creacion_naive, ahora)

    # Consultar las próximas citas programadas (estado "P") en orden descendente
    proximas_citas = CitaMedica.objects.filter(
      fecha__gte=ahora.date(),
      estado='P'
    ).order_by('fecha', 'hora_cita')[:3]

    # Obtener los meses del año
    meses = [(i, calendar.month_name[i]) for i in range(1, 13)]

    # Estadísticas de Atenciones por mes
    atenciones_por_mes = (
      Atencion.objects
      .extra(select={'mes': "EXTRACT(month FROM fecha_atencion)"})
      .values('mes')
      .annotate(conteo=Count('id'))
      .order_by('mes')
    )
    atenciones_data = [0] * 12
    for atencion in atenciones_por_mes:
      atenciones_data[int(atencion['mes']) - 1] = atencion['conteo']

    # Estadísticas de Citas por estado
    citas_data = [
      CitaMedica.objects.filter(estado='P').count(),  # Programada
      CitaMedica.objects.filter(estado='C').count(),  # Cancelada
      CitaMedica.objects.filter(estado='R').count()  # Realizada
    ]

    # Agregar todos los datos al contexto
    context.update({
      "title1": "SaludSync",
      "title2": "Sistema Medico",
      "can_paci": Paciente.cantidad_pacientes(),
      "can_citas": CitaMedica.cantidad_disponible_hoy(),
      "can_atencion": Atencion.cantidad(),
      "ultima_atencion": ultima_atencion,
      "tiempo_desde_ultima_atencion": tiempo_desde_ultima_atencion,
      "proximas_citas": proximas_citas,
      "ultima_cita_realizada": ultima_cita_realizada,
      "tiempo_desde_ultima_cita": tiempo_desde_ultima_cita,
      "ultimo_paciente": ultimo_paciente,
      "tiempo_desde_ultimo_paciente": tiempo_desde_ultimo_paciente,
      "meses": meses,
      "atenciones_data": atenciones_data,
      "citas_data": citas_data,
    })

    return context


def filter_atenciones(request):
  mes = request.GET.get('mes')
  if mes:
    atenciones = Atencion.objects.filter(
      fecha_atencion__month=mes
    ).count()
    return JsonResponse(atenciones, safe=False)
  return JsonResponse(0, safe=False)


def filter_citas(request):
  mes = request.GET.get('mes')
  if mes:
    citas_por_estado = {
      'P': CitaMedica.objects.filter(fecha__month=mes, estado='P').count(),
      'C': CitaMedica.objects.filter(fecha__month=mes, estado='C').count(),
      'R': CitaMedica.objects.filter(fecha__month=mes, estado='R').count()
    }
    return JsonResponse(citas_por_estado)
  return JsonResponse({'P': 0, 'C': 0, 'R': 0})


def filter_citas_estado(request):
  estado = request.GET.get('estado')
  mes = request.GET.get('mes')

  if estado and mes:
    citas = CitaMedica.objects.filter(
      estado=estado,
      fecha__month=mes
    ).count()

    # Crear array con el conteo en la posición correcta
    resultado = [0, 0, 0]
    if estado == 'P':
      resultado[0] = citas
    elif estado == 'C':
      resultado[1] = citas
    elif estado == 'R':
      resultado[2] = citas

    return JsonResponse(resultado, safe=False)
  return JsonResponse([0, 0, 0], safe=False)
