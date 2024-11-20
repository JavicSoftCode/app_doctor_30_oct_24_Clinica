# # from django.shortcuts import render, get_object_or_404
# # from django.http import JsonResponse
# #
# # from aplication.core.models import Doctor
# #
# #
# # def agendar_cita(request, doctor_id):
# #   doctor = get_object_or_404(Doctor, id=doctor_id)
# #   horario_atencion = doctor.horario_atencion  # JSONField con los horarios
# #   return render(request, 'attention/agendar_citas/agendar_citas.html',
# #                 {'doctor': doctor, 'horario_atencion': horario_atencion})
# #
# #
# # def confirmar_cita(request):
# #   if request.method == 'POST':
# #     data = json.loads(request.body)
# #     fecha = data.get('fecha')
# #     hora = data.get('hora')
# #     # Aquí puedes guardar la cita en tu modelo de paciente
# #     return JsonResponse({'status': 'success', 'message': 'Cita confirmada'})
# #   return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
#
# from datetime import datetime
#
# from django.http import JsonResponse
# from django.views import View
#
# from aplication.attention.models import HorarioAtencion, RegistroHorasDoctor
#
#
# class GuardarRegistroHorasView(View):
#   def get(self, request, *args, **kwargs):
#     # Para pruebas, podemos devolver un mensaje indicando que solo aceptamos POST
#     return JsonResponse({"error": "Este endpoint solo acepta solicitudes POST."}, status=405)
#
#   def post(self, request, *args, **kwargs):
#     # Obtenemos los datos enviados en el cuerpo de la solicitud
#     data = request.POST.get("horario_atencion_input")
#     if not data:
#       return JsonResponse({"error": "No se enviaron datos."}, status=400)
#
#     try:
#       # Intentamos convertir el JSON recibido a un diccionario
#       registros = json.loads(data)
#     except json.JSONDecodeError:
#       return JsonResponse({"error": "El formato del JSON no es válido."}, status=400)
#
#     # Validamos que los datos tengan el formato esperado
#     if not isinstance(registros, dict):
#       return JsonResponse({"error": "Los datos enviados no tienen el formato esperado."}, status=400)
#
#     errores = []  # Lista para guardar errores relacionados con días no válidos
#     try:
#       for fecha_str, horas in registros.items():
#         try:
#           # Convertimos la fecha de texto a objeto `date`
#           fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
#         except ValueError:
#           errores.append(f"Formato de fecha inválido: {fecha_str}")
#           continue
#
#         dia_semana = fecha.strftime("%A")  # Obtenemos el día de la semana
#
#         try:
#           # Obtenemos el horario de atención correspondiente al día de la semana
#           horario = HorarioAtencion.objects.get(dia_semana=dia_semana)
#           # Creamos el registro de horas
#           RegistroHorasDoctor.objects.create(
#             horario=horario,
#             fecha=fecha,
#             horas_trabajadas=horas,
#           )
#         except HorarioAtencion.DoesNotExist:
#           errores.append(f"No se encontró horario para el día: {dia_semana}")
#           continue
#
#       # Retornamos una respuesta de éxito con errores no críticos
#       return JsonResponse({
#         "success": "Registros guardados correctamente.",
#         "errores": errores,
#       })
#     except Exception as e:
#       # Retornamos un mensaje genérico en caso de un error inesperado
#       return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)
