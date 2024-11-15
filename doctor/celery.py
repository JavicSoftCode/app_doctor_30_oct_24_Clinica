# doctor/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Configuración del archivo settings de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor.settings')
app = Celery('doctor')

# Configuración de Celery para usar el archivo de configuración de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuración de tiempo de espera para Redis en Celery
CELERY_BROKER_TRANSPORT_OPTIONS = {'socket_timeout': 30}  # tiempo en segundos
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {'socket_timeout': 30}

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 3,  # Número de reintentos antes de fallar
    'retry_on_timeout': True
}


# Detectar y registrar automáticamente tareas de los apps instalados
app.autodiscover_tasks()
