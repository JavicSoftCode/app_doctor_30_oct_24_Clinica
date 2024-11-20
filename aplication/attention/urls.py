from django.urls import path

from aplication.attention.views.citaMedica import *  #
from aplication.attention.views.examenSolicitado import *  #
from aplication.attention.views.medical_attention import *  #
from aplication.attention.views.serviciosAdicionales import *
from aplication.attention.views.costoAtencion import *
# from aplication.attention.views.agendar_citas import *

app_name = 'attention'
urlpatterns = [

  # URLs cita medica
  path('citaMedica_list/', CitaMedicaListView.as_view(), name='citaMedica_list'),
  path('citaMedica_create/', CitaMedicaCreateView.as_view(), name='citaMedica_create'),
  path('citaMedica_update/<int:pk>/', CitaMedicaUpdateView.as_view(), name='citaMedica_update'),
  path('citaMedica_delete/<int:pk>/', CitaMedicaDeleteView.as_view(), name='citaMedica_delete'),
  path('citaMedica_detail/<int:pk>/', CitaMedicaDetailView.as_view(), name='citaMedica_detail'),

  # Urls de atencion
  path('attention_list/', AttentionListView.as_view(), name="attention_list"),
  path('attention_create/', AttentionCreateView.as_view(), name="attention_create"),
  path('attention_update/<int:pk>/', AttentionUpdateView.as_view(), name='attention_update'),
  path('attention_detail/<int:pk>/', AttentionDetailView.as_view(), name='attention_detail'),

  # pdf
  path('attention_view/<int:pk>/certificado', ViewAtencionPdf.as_view(), name='attention_view_certificado'),
  # path('attention_descargar', generar_certificado_pdf, name='attention_descargar'),
  path('attention_descargar/<int:pk>/', generar_certificado_pdf, name='attention_descargar'),

  # URLs examen solicitado
  path('examenSolicitado_list/', ExamenSolicitadoListView.as_view(), name='examenSolicitado_list'),
  path('examenSolicitado_create/', ExamenSolicitadoCreateView.as_view(), name='examenSolicitado_create'),
  path('examenSolicitado_update/<int:pk>/', ExamenSolicitadoUpdateView.as_view(), name='examenSolicitado_update'),
  path('examenSolicitado_subir/<int:pk>/', ExamenSolicitadoResultView.as_view(), name='examenSolicitado_subir'),
  path('examenSolicitado_resultado/<int:pk>/', ExamenResultadoDetailView.as_view(), name='examenSolicitado_resultado'),
  path('examenSolicitado_delete/<int:pk>/', ExamenSolicitadoDeleteView.as_view(), name='examenSolicitado_delete'),
  path('examenSolicitado_detail/<int:pk>/', ExamenSolicitadoDetailView.as_view(), name='examenSolicitado_detail'),

  # URLs servicios adicionales
  path('serviciosAdicionales_list/', ServiciosAdicionalesListView.as_view(), name='serviciosAdicionales_list'),
  path('serviciosAdicionales_create/', ServiciosAdicionalesCreateView.as_view(), name='serviciosAdicionales_create'),
  path('serviciosAdicionales_update/<int:pk>/', ServiciosAdicionalesUpdateView.as_view(),
       name='serviciosAdicionales_update'),
  path('serviciosAdicionales_delete/<int:pk>/', ServiciosAdicionalesDeleteView.as_view(),
       name='serviciosAdicionales_delete'),
  path('serviciosAdicionales_detail/<int:pk>/', ServiciosAdicionalesDetailView.as_view(),
       name='serviciosAdicionales_detail'),

  path('factura/<int:atencion_id>/', generar_factura, name='generar_factura'),

  # path('costos/', CostosListView.as_view(), name='costos_list'),
  # path('costos/<int:pk>/update/', CostoAtencionUpdateView.as_view(), name='costo_update'),
  # path('costos/<int:pk>/pagar/', marcar_pagado, name='marcar_pagado'),
  path('costos_atencion/', CostosAtencionListView.as_view(), name='costos_atencion_list'),
  path('costos_atencion/pagar/<int:pk>/', PagarCostoAtencionView.as_view(), name='costos_atencion_pagar'),

  # path('agendar-cita/<int:doctor_id>/', agendar_cita, name='agendar_cita'),
  # path('confirmar-cita/', confirmar_cita, name='confirmar_cita'),
  # path('guardarRegistroHorasView/', GuardarRegistroHorasView.as_view(), name='guardar_registro_horas'),
]
