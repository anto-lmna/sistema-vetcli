from django.urls import path
from .views import HistoriaClinicaCreateView, HistoriaDetailView

app_name = "historias"
urlpatterns = [
    # Crear Archivo
    path(
        "crear/<int:mascota_id>/",
        HistoriaClinicaCreateView.as_view(),
        name="crear_historia",
    ),
    # Ver en la web
    path("detalle/<int:pk>/", HistoriaDetailView.as_view(), name="historia_detalle"),
]
