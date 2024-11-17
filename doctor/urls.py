from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from aplication.security.views.modulos import ModuloTemplateView

urlpatterns = [
                path('admin/', admin.site.urls),
                path('', include('aplication.core.urls', namespace='core')),
                path('', include('aplication.attention.urls', namespace='attention')),
                path('modulos/', ModuloTemplateView.as_view(), name='modulos'),
                path('security/', include('aplication.security.urls', namespace='security')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
