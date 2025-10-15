from django.urls import path
from . import views

app_name = "turnos"

urlpatterns = [
    # Veterinario
    path(
        "disponibilidades/",
        views.DisponibilidadListView.as_view(),
        name="disponibilidades",
    ),
    path(
        "disponibilidades/nueva/",
        views.DisponibilidadCreateView.as_view(),
        name="nueva_disponibilidad",
    ),
    path("agenda/", views.AgendaVeterinarioView.as_view(), name="agenda_vet"),
    path("agenda/datos/", views.TurnosJSONView.as_view(), name="turnos_json"),
    # Cliente
    path("disponibles/", views.TurnosDisponiblesListView.as_view(), name="disponibles"),
    path("mis-turnos/", views.MisTurnosListView.as_view(), name="mis_turnos"),
    path("<int:pk>/reservar/", views.TurnoReservarView.as_view(), name="reservar"),
    # Admin
    path("agenda-clinica/", views.AgendaClinicaView.as_view(), name="agenda_clinica"),
    path(
        "agenda-clinica/datos/",
        views.TurnosClinicaJSONView.as_view(),
        name="turnos_clinica_json",
    ),
]
