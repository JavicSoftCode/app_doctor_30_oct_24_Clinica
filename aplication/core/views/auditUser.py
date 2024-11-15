from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic import ListView, DetailView

from aplication.core.models import AuditUser
from doctor.mixins import ListViewMixin


class AuditUserListView(LoginRequiredMixin, ListViewMixin, ListView):
  template_name = "core/auditUser/list.html"
  model = AuditUser
  context_object_name = 'auditorias'

  def get_queryset(self):
    # Inicializa la query como una combinación vacía
    self.query = Q()
    q1 = self.request.GET.get('q')
    accion_filter = self.request.GET.get('acciones')

    # Filtra por ID si `q` es un dígito, o realiza búsquedas parciales en otros campos
    if q1:
      if q1.isdigit():
        self.query.add(Q(id=q1), Q.AND)
      else:
        self.query |= Q(usuario__username__icontains=q1)
        self.query |= Q(tabla__icontains=q1)
        self.query |= Q(registroid__icontains=q1)

    # Filtra por acción específica si coincide con "A", "M" o "E"
    if accion_filter in ["A", "M", "E"]:
      self.query &= Q(accion=accion_filter)

    # Ordena los resultados por fecha y hora
    return self.model.objects.filter(self.query).order_by('fecha', 'hora')


class AuditUserDetailView(LoginRequiredMixin, DetailView):
  model = AuditUser
  extra_context = {
    "detail": "Detalles de la Auditoria de Usuario"
  }

  def get(self, request, *args, **kwargs):
    # Obtiene el objeto de auditoría y lo retorna en formato JSON
    auditUser = self.get_object()
    data = {
      'id': auditUser.id,
      'usuario': auditUser.usuario.username,
      'tabla': auditUser.tabla,
      'registroid': auditUser.registroid,
      'accion': auditUser.accion,
      'fecha': auditUser.fecha,
      'hora': auditUser.hora,
      'estacion': auditUser.estacion,
    }
    return JsonResponse(data)
