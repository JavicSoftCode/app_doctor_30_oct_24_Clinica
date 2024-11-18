from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Atencion, CostosAtencion

@receiver(post_save, sender=Atencion)
def crear_costos_atencion(sender, instance, created, **kwargs):
    """Crea automáticamente un registro de CostosAtencion si no existe."""
    if created and not instance.costos_atencion.exists():
        CostosAtencion.objects.create(atencion=instance)
