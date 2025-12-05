from django.urls import path
from .views import HistoriaClinicaCreateView, HistoriaDetailView, MisHistoriasListView

app_name = "historias"
urlpatterns = [
    path(
        "crear/<int:mascota_id>/",
        HistoriaClinicaCreateView.as_view(),
        name="crear_historia",
    ),
    path("detalle/<int:pk>/", HistoriaDetailView.as_view(), name="historia_detalle"),
    path("mis-registros/", MisHistoriasListView.as_view(), name="mis_historias"),
]
