# # views.py
# import json
#
# import requests
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
#
# from aplication.attention.models import Factura
#
#
# class PayPalClient:
#   def __init__(self):
#     self.client_id = settings.PAYPAL_CLIENT_ID
#     self.client_secret = settings.PAYPAL_CLIENT_SECRET
#     self.base_url = "https://api-m.sandbox.paypal.com"  # Cambia a api-m.paypal.com para producción
#
#   def get_access_token(self):
#     auth_url = f"{self.base_url}/v1/oauth2/token"
#     headers = {
#       "Accept": "application/json",
#       "Accept-Language": "en_US"
#     }
#     data = {
#       "grant_type": "client_credentials"
#     }
#     response = requests.post(
#       auth_url,
#       headers=headers,
#       data=data,
#       auth=(self.client_id, self.client_secret)
#     )
#     return response.json()["access_token"]
#
#
# @csrf_exempt
# def create_paypal_order(request):
#   if request.method == "POST":
#     try:
#       data = json.loads(request.body)
#       monto = data.get('monto')
#       factura_id = data.get('factura_id')
#
#       paypal_client = PayPalClient()
#       access_token = paypal_client.get_access_token()
#
#       headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {access_token}",
#       }
#
#       order_data = {
#         "intent": "CAPTURE",
#         "purchase_units": [{
#           "amount": {
#             "currency_code": "USD",
#             "value": str(monto)
#           },
#           "description": f"Factura #{factura_id}"
#         }]
#       }
#
#       response = requests.post(
#         f"{paypal_client.base_url}/v2/checkout/orders",
#         headers=headers,
#         json=order_data
#       )
#
#       if response.status_code == 201:
#         return JsonResponse(response.json())
#       else:
#         return JsonResponse({
#           "error": "Error al crear la orden"
#         }, status=400)
#
#     except Exception as e:
#       return JsonResponse({
#         "error": str(e)
#       }, status=400)
#
#   return JsonResponse({"error": "Método no permitido"}, status=405)
#
#
# @csrf_exempt
# def capture_paypal_order(request, order_id):
#   if request.method == "POST":
#     try:
#       paypal_client = PayPalClient()
#       access_token = paypal_client.get_access_token()
#
#       headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {access_token}",
#       }
#
#       response = requests.post(
#         f"{paypal_client.base_url}/v2/checkout/orders/{order_id}/capture",
#         headers=headers
#       )
#
#       if response.status_code == 201:
#         # El pago fue exitoso, actualiza la factura
#         response_data = response.json()
#         purchase_unit = response_data["purchase_units"][0]
#         factura_id = purchase_unit["description"].split("#")[1]
#
#         factura = Factura.objects.get(id=factura_id)
#         factura.estado = "PAGADA"
#         factura.referencia_pago = order_id
#         factura.save()
#
#         return JsonResponse(response_data)
#       else:
#         return JsonResponse({
#           "error": "Error al capturar el pago"
#         }, status=400)
#
#     except Exception as e:
#       return JsonResponse({
#         "error": str(e)
#       }, status=400)
#
#   return JsonResponse({"error": "Método no permitido"}, status=405)
