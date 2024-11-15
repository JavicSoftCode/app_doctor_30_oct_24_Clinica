# # aplication/attention/tasks.py
# from datetime import timedelta
#
# from celery import shared_task
# from django.core.mail import send_mail
# from django.utils import timezone
#
# from aplication.attention.models import CitaMedica
#
#
# @shared_task
# def enviar_recordatorio_cita():
#   # Calcular el día siguiente
#   manana = timezone.now().date() + timedelta(days=1)
#   citas_manana = CitaMedica.objects.filter(fecha=manana, estado='P')
#
#   for cita in citas_manana:
#     paciente = cita.paciente
#     if paciente.email:
#       asunto = "Recordatorio de Cita Médica"
#       mensaje = f"Estimado(a) {paciente.nombre_completo}, le recordamos que tiene una cita programada para el {cita.fecha} a las {cita.hora_cita}."
#       remitente = 'ing.javiersistem02ejqp@gmail.com'  # Cambiar a un correo válido
#       destinatario = [paciente.email]
#
#       send_mail(asunto, mensaje, remitente, destinatario, fail_silently=False)


# aplication/attention/tasks.py
from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from aplication.attention.models import CitaMedica


@shared_task
def enviar_recordatorio_cita():
  # Calcular el tiempo para 5 minutos antes de la cita
  ahora = timezone.now()
  cinco_minutos_despues = ahora + timedelta(days=1)
                                                                                      # minutes=5
  # Buscar citas dentro de los próximos 5 minutos
  citas_proximas = CitaMedica.objects.filter(
    fecha=ahora.date(),
    hora_cita__range=(ahora.time(), cinco_minutos_despues.time()),
    estado='P'
  )

  for cita in citas_proximas:
    paciente = cita.paciente
    if paciente.email:
      asunto = "Recordatorio de Cita Médica"
      mensaje = f"Estimado(a) {paciente.nombre_completo}, le recordamos que tiene una cita programada para hoy a las {cita.hora_cita}."
      remitente = 'ing.javiersistem02ejqp@gmail.com'
      destinatario = [paciente.email]

      send_mail(asunto, mensaje, remitente, destinatario, fail_silently=False)

# def enviar_recordatorio_cita():
#     # Calcular el tiempo para pruebas (por ejemplo, dentro de una hora)
#     ahora = timezone.now()
#     una_hora_despues = ahora + timedelta(hours=1)
#
#     # Buscar citas dentro de la próxima hora
#     citas_proximas = CitaMedica.objects.filter(
#         fecha=ahora.date(),
#         hora_cita__range=(ahora.time(), una_hora_despues.time()),
#         estado='P'
#     )
#
#     for cita in citas_proximas:
#         paciente = cita.paciente
#         if paciente.email:
#             asunto = "Recordatorio de Cita Médica"
#             mensaje = f"Estimado(a) {paciente.nombre_completo}, le recordamos que tiene una cita programada para hoy a las {cita.hora_cita}."
#             remitente = 'ing.javiersistem02ejqp@gmail.com'
#             destinatario = [paciente.email]
#
#             send_mail(asunto, mensaje, remitente, destinatario, fail_silently=False)
