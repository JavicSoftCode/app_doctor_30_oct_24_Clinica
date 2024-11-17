from crum import get_current_request
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.db import models
from django.forms import model_to_dict
from django.utils.html import mark_safe


class Menu(models.Model):
  name = models.CharField(verbose_name='Nombre', max_length=150, unique=True)
  icon = models.CharField(verbose_name='Icono', max_length=100)

  def __str__(self):
    return self.name

  def get_model_to_dict(self):
    item = model_to_dict(self)
    return item

  def get_icon(self):
    if self.icon:
      return self.icon
    return 'bi bi-calendar-x-fill'

  def has_related_objects(self):
    if Module.objects.filter(menu=self).exists():
      return True
    return False

  class Meta:
    verbose_name = 'Menu'
    verbose_name_plural = 'Menus'
    ordering = ['-name']


# permisos: add_empleado, view_empleado, change_empleado, delete_empleado
class Module(models.Model):
  url = models.CharField(verbose_name='Url', max_length=100, unique=True)
  name = models.CharField(verbose_name='Nombre', max_length=100)
  menu = models.ForeignKey(Menu, on_delete=models.PROTECT, verbose_name='Menu')
  description = models.CharField(
    verbose_name='Descripción',
    max_length=200,
    null=True,
    blank=True
  )
  icon = models.CharField(verbose_name='Icono', max_length=100, null=True,
                          blank=True)
  is_active = models.BooleanField(verbose_name='Es activo', default=True)
  permissions = models.ManyToManyField(
    verbose_name='Permisos',
    to=Permission,
    blank=True
  )

  def __str__(self):
    return '{} [{}]'.format(self.name, self.url)

  def get_model_to_dict(self):
    item = model_to_dict(self)
    return item

  def has_related_objects_Modules(self):
    return GroupModulePermission.objects.filter(module=self).exists()

  def get_icon(self):
    if self.icon:
      return self.icon
    return 'bi bi-x-octagon'

  def get_permissions_display(self):
    """
    Retorna los permisos asociados como una lista concatenada o un mensaje por defecto.
    """
    if self.permissions.exists():
      return ' -- '.join(permission.name for permission in self.permissions.all())
    return "No tiene permisos asignados"

  class Meta:
    verbose_name = 'Modulo'
    verbose_name_plural = 'Modulos'
    ordering = ('-name',)


class GroupModulePermission(models.Model):
  group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Grupo')
  module = models.ForeignKey(Module, on_delete=models.PROTECT, verbose_name='Modulo')
  permissions = models.ManyToManyField(Permission)

  def __str__(self):
    return f"{self.module.name} -{self.group.name}"

  def get_permissions_display(self):
    """
    Retorna los permisos asociados como una lista concatenada o un mensaje por defecto.
    """
    if self.permissions.exists():
      return mark_safe(" --  ".join(permission.name for permission in self.permissions.all()))
    return "No tiene permisos asignados"

  # def get_permissions_display(self):
  #   Une los nombres de los permisos con un salto de línea HTML
  # return mark_safe("<br>".join(permission.name for permission in self.permissions.all()))

  def get_group_module_permission_active_list(group_id):
    return GroupModulePermission.objects.select_related(
      'module',
      'module__menu'
    ).filter(
      group_id=group_id,
      module__is_active=True
    )

  class Meta:
    verbose_name = 'Grupo Módulo Permiso'
    verbose_name_plural = 'Grupos Módulo Permisos'
    ordering = ('-id',)


class User(AbstractUser):
  dni = models.CharField(verbose_name='Cédula o RUC', max_length=13, blank=True, null=True, unique=True)
  image = models.ImageField(
    verbose_name='Archive image',
    upload_to='users/',
    max_length=1024,
    blank=True,
    null=True
  )
  email = models.EmailField('Email', unique=True)
  direction = models.CharField('Direccion', max_length=200, blank=True, null=True)
  phone = models.CharField('Telefono', max_length=50, blank=True, null=True)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["username", "first_name", "last_name"]

  class Meta:
    verbose_name = "Usuario"
    verbose_name_plural = "Usuarios"
    # Crea un nuevo permiso al modelo
    permissions = (
      ("change_userprofile", f"Cambiar perfil {verbose_name}"),
      ("change_userpassword", f"Cambiar password {verbose_name}"),
    )

  def __str__(self):
    return f'{self.username}'

  @property
  def get_full_name(self):
    return f"{self.first_name} {self.last_name}"

  # def get_groups(self):
  #   return f'{self.groups.all()}'
  def get_groups(self):
    groups = self.groups.all()
    if groups.exists():
      return ', '.join(group.name for group in groups)
    return "No pertenece a ningún grupo"

  def get_short_name(self):
    return self.username

  def get_group_session(self):
    """Devuelve el objeto 'Group' completo en lugar de un diccionario."""
    request = get_current_request()
    group_id = request.session.get('group_id')
    if group_id:
      try:
        return Group.objects.get(pk=group_id)
      except Group.DoesNotExist:
        return None
    return None

  def set_group_session(self):
    """Establece el grupo en la sesión usando solo datos serializables."""
    request = get_current_request()
    if 'group_id' not in request.session:
      groups = self.groups.all().order_by('id')
      if groups.exists():
        first_group = groups.first()
        request.session['group_id'] = first_group.id
        request.session['group_name'] = first_group.name

  def get_image(self):
    if self.image:
      return self.image.url
    else:
      return '/static/img/usuario_anonimo.png'


class AuditUser(models.Model):
  TIPOS_ACCIONES = (
    ('A', 'A'),  # Adicion
    ('M', 'M'),  # Modificacion
    ('E', 'E')  # Eliminacion
  )
  usuario = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.PROTECT)
  tabla = models.CharField(max_length=100, verbose_name='Tabla')
  registroid = models.IntegerField(verbose_name='Registro Id')
  accion = models.CharField(choices=TIPOS_ACCIONES, max_length=10, verbose_name='Accion')
  fecha = models.DateField(verbose_name='Fecha')
  hora = models.TimeField(verbose_name='Hora')
  estacion = models.CharField(max_length=100, verbose_name='Estacion')

  def __str__(self):
    return "{} - {} [{}]".format(self.usuario.username, self.tabla, self.accion)

  class Meta:
    verbose_name = 'Auditoria Usuario '
    verbose_name_plural = 'Auditorias Usuarios'
    ordering = ('-fecha', 'hora')
