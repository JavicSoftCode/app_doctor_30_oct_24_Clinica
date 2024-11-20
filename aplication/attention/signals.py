# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from .models import Atencion, CostosAtencion
#
#
# @receiver(post_save, sender=Atencion)
# def crear_costos_atencion(sender, instance, created, **kwargs):
#   """Crea automáticamente un registro de CostosAtencion si no existe."""
#   if created and not instance.costos_atencion.exists():
#     CostosAtencion.objects.create(atencion=instance)
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from aplication.attention.models import Atencion, DetalleAtencion


def recalcular_costo_atencion(atencion):
    """Recalcula el costo total de los medicamentos y servicios adicionales."""
    try:
        # Costo total de medicamentos
        costo_medicamentos = sum(
            detalle.cantidad * detalle.medicamento.precio
            for detalle in atencion.atenciones.select_related('medicamento').all()
        )

        # Costo total de servicios adicionales
        costo_servicios = sum(
            servicio.costo_servicio for servicio in atencion.servicios_adicionales.all()
        )

        costo_doctor = 20

        # Retorna el total como Decimal
        total = costo_medicamentos + costo_servicios  + costo_doctor

        # Actualiza el campo total en el modelo relacionado (si aplica)
        # Aquí podrías guardar el total en otro modelo si es necesario
        print(f"Nuevo costo total para la atención {atencion.id}: {total}")

    except Exception as e:
        print(f"Error al recalcular costos: {e}")


@receiver(post_save, sender=DetalleAtencion)
def actualizar_costo_detalle(sender, instance, **kwargs):
    """Actualiza el costo total cuando se guarda un DetalleAtencion."""
    recalcular_costo_atencion(instance.atencion)


@receiver(m2m_changed, sender=Atencion.servicios_adicionales.through)
def actualizar_costo_servicios(sender, instance, action, **kwargs):
    """Actualiza el costo total cuando cambian los servicios adicionales."""
    if action in ['post_add', 'post_remove', 'post_clear']:
        recalcular_costo_atencion(instance)
