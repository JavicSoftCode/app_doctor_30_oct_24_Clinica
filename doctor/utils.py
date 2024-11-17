import random
import re
import string
from datetime import date
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(regex=r'^\d{9,15}$', message="Caracteres inválidos para un número de teléfono.")


def valida_numero_entero_positivo(value):
  if not str(value).isdigit() or int(value) <= 0:
    raise ValidationError('Debe ingresar un número entero positivo válido.')


def valida_numero_decimal_positivo(value):
  try:
    value = Decimal(value)
  except InvalidOperation:
    # Mensaje de error personalizado sin el nombre del campo
    raise ValidationError("Debe ingresar un número positivo en el Costo del Servicio.")

  if value <= 0:
    raise ValidationError("Debe ingresar un número positivo en el Costo del Servicio.")
  elif value.as_tuple().exponent < -2:
    raise ValidationError("El número no puede tener más de dos decimales en el Costo del Servicio.")


def valida_numero_flotante_positivo(value):
  try:
    valor_float = float(value)
    if valor_float <= 0:
      raise ValidationError('Debe ingresar un número flotante positivo válido.')
  except ValueError:
    raise ValidationError('Debe ingresar un número flotante válido.')


def custom_serializer(obj):
  if isinstance(obj, Decimal):
    return str(obj)
  if isinstance(obj, datetime):
    return obj.isoformat()
  raise TypeError(f"Type {type(obj)} not serializable")


def save_audit(request, model, action):
  from aplication.security.models import AuditUser
  user = request.user
  # Obtain client ip address
  client_address = ip_client_address(request)
  # Registro en tabla Auditora BD
  auditusuariotabla = AuditUser(usuario=user,
                                tabla=model.__class__.__name__,
                                registroid=model.id,
                                accion=action,
                                fecha=timezone.now().date(),
                                hora=timezone.now().time(),
                                estacion=client_address)
  auditusuariotabla.save()


# Obtener el IP desde donde se esta accediendo
def ip_client_address(request):
  try:
    # case server externo
    client_address = request.META['HTTP_X_FORWARDED_FOR']
  except:
    # case localhost o 127.0.0.1
    client_address = request.META['REMOTE_ADDR']

  return client_address


def validate_not_empty(value, field_name):
  value = value.strip()
  if not value:
    print(f"El campo {field_name} está vacío.")  # Usar logger en lugar de print
    raise ValidationError(_(f"El campo {field_name} no puede estar vacío."))
  return value


def valida_cedula(value):
  value = validate_not_empty(value, "cédula")  # Validar que no esté vacío
  cedula = str(value)

  if not cedula.isdigit():
    raise ValidationError('La cédula debe contener solo números.')

  longitud = len(cedula)
  if longitud != 10:
    raise ValidationError('Cantidad de dígitos incorrecta.')

  coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
  total = 0
  for i in range(9):
    digito = int(cedula[i])
    coeficiente = coeficientes[i]
    producto = digito * coeficiente
    if producto > 9:
      producto -= 9
    total += producto

  digito_verificador = (total * 9) % 10
  if digito_verificador != int(cedula[9]):
    raise ValidationError('La cédula no es válida.')


def validate_full_name(value):
  value = validate_not_empty(value, "nombre completo")  # Validar que no esté vacío
  value = value.strip()  # Eliminar espacios en blanco
  MinLengthValidator(3, _("El nombre o apellido debe tener al menos 3 caracteres."))(value)

  words = value.split()
  if len(words) < 2 or any(len(word) < 2 for word in words):
    raise ValidationError(
      _("Debe ingresar los dos nombres o apellidos, y cada uno debe tener al menos 2 caracteres.")
    )


def validate_birth_date(value):
  if not value:
    raise ValidationError(_("No se aceptan campos vacíos."))
  if value >= timezone.now().date():
    raise ValidationError(_("La fecha no puede ser en futuro."))

  today = date.today()
  age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
  if age < 18:
    raise ValidationError(_("Mayor a 18 años."))


def validate_and_format_cell_number(cell):
  cell = validate_not_empty(cell, "número de celular")

  pattern = re.compile(r'^(?:\+593\s?9\d{8}|09\d{8}|(?:\+593)?9\d{8})$')
  if not pattern.match(cell):
    print("Número de celular inválido.")
    raise ValidationError(_("El número de celular debe tener 9 dígitos después del código de país (+593)."))

  if cell.startswith("09"):
    formatted_cell = "+593 " + cell[1:]
  elif cell.startswith("+593"):
    formatted_cell = "+593 " + cell[4:]
  else:
    print("Formato de número de celular inválido.")
    raise ValidationError(_("Formato de número de celular no válido."))

  return formatted_cell


def validate_codigo_unico_doctor(codigo):
  codigo = validate_not_empty(codigo, "código único del doctor")

  # Verificar que el código tenga al menos 12 dígitos
  if len(codigo) < 12:
    print("Código único del doctor inválido.")
    raise ValidationError(_("El código único del doctor debe tener al menos 12 dígitos."))

  # Verificar que solo contenga dígitos
  if not codigo.isdigit():
    raise ValidationError(_("El código único del doctor debe contener solo números."))

  return codigo


def validate_sueldo(sueldo):
  # Verificar que el sueldo no esté vacío
  if sueldo is None:
    raise ValidationError(_("El sueldo no puede estar vacío."))

  # Verificar que el sueldo sea un número decimal válido
  try:
    sueldo_decimal = Decimal(sueldo)
  except (ValueError, TypeError, InvalidOperation):
    raise ValidationError(_("El sueldo debe ser un número válido."))

  # Verificar que el sueldo tenga como máximo 2 decimales
  if sueldo_decimal.as_tuple().exponent < -2:
    raise ValidationError(_("El sueldo no debe tener más de 2 decimales."))

  # Verificar que el sueldo sea mayor o igual a 450
  if sueldo_decimal < 450:
    raise ValidationError(_("El sueldo no debe ser menor a $450."))

  return sueldo_decimal


def validate_precio(precio):
  # Verificar que el precio no esté vacío
  if precio is None:
    raise ValidationError(_("El precio no puede estar vacío."))

  # Verificar que el precio sea un número decimal válido
  try:
    precio_decimal = Decimal(precio)
  except (ValueError, TypeError, InvalidOperation):
    raise ValidationError(_("El precio debe ser un número válido."))

  # Verificar que el precio tenga como máximo 2 decimales
  if precio_decimal.as_tuple().exponent < -2:
    raise ValidationError(_("El precio no debe tener más de 2 decimales."))

  # Verificar que el precio sea mayor o igual a 0.50
  if precio_decimal < Decimal("0.50"):
    raise ValidationError(_("El precio debe ser mayor o igual a $0.50."))

  # Verificar que el precio no tenga caracteres especiales (solo números y punto decimal)
  if not str(precio_decimal).replace('.', '').isdigit():
    raise ValidationError(_("El precio solo debe contener números y una coma decimal."))

  return precio_decimal


def validate_cantidad(cantidad):
  # Verificar que la cantidad no esté vacía
  if cantidad is None:
    raise ValidationError(_("La cantidad no puede estar vacía."))

  # Verificar que la cantidad sea un número entero válido
  if not isinstance(cantidad, int):
    raise ValidationError(_("La cantidad debe ser un número entero."))

  # Verificar que la cantidad sea mayor o igual a 1
  if cantidad < 1:
    raise ValidationError(_("La cantidad debe ser al menos 1."))

  return cantidad


def generate_valid_diagnosis_code():
  prefix = "JSC-10"
  # Genera 4 caracteres alfanuméricos para la primera parte
  part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
  # Genera 5 caracteres alfanuméricos para la segunda parte
  part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
  # Devuelve el código completo en el formato requerido
  return f"{prefix}-{part1}-{part2}"
