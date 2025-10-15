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
    path(
        "disponibilidades/<int:pk>/eliminar/",
        views.DisponibilidadDeleteView.as_view(),
        name="eliminar_disponibilidad",
    ),
    path("agenda/", views.AgendaVeterinarioView.as_view(), name="agenda_vet"),
    path("agenda/datos/", views.TurnosJSONView.as_view(), name="turnos_json"),
    path(
        "turno/<int:pk>/detalle-vet/",
        views.TurnoDetalleVeterinarioView.as_view(),
        name="turno_detalle_vet",
    ),
    path(
        "turno/<int:pk>/iniciar/",
        views.TurnoIniciarAtencionView.as_view(),
        name="turno_iniciar",
    ),
    path(
        "turno/<int:pk>/completar/",
        views.TurnoCompletarView.as_view(),
        name="turno_completar",
    ),
    path(
        "turno/<int:pk>/no-asistio/",
        views.TurnoNoAsistioView.as_view(),
        name="turno_no_asistio",
    ),
    # Cliente
    path("disponibles/", views.TurnosDisponiblesListView.as_view(), name="disponibles"),
    path("mis-turnos/", views.MisTurnosListView.as_view(), name="mis_turnos"),
    path("<int:pk>/reservar/", views.TurnoReservarView.as_view(), name="reservar"),
    path(
        "turno/<int:pk>/detalle-cliente/",
        views.TurnoDetalleClienteView.as_view(),
        name="turno_detalle_cliente",
    ),
    path(
        "turno/<int:pk>/cancelar-cliente/",
        views.TurnoCancelarClienteView.as_view(),
        name="turno_cancelar_cliente",
    ),
    # Administrador
    path("agenda-clinica/", views.AgendaClinicaView.as_view(), name="agenda_clinica"),
    path(
        "agenda-clinica/datos/",
        views.TurnosClinicaJSONView.as_view(),
        name="turnos_clinica_json",
    ),
    path(
        "turno/<int:pk>/detalle-admin/",
        views.TurnoDetalleAdminView.as_view(),
        name="turno_detalle_admin",
    ),
    path(
        "turno/<int:pk>/cancelar-admin/",
        views.TurnoCancelarAdminView.as_view(),
        name="turno_cancelar_admin",
    ),
    path("turno/crear/", views.TurnoCrearAdminView.as_view(), name="turno_crear_admin"),
]
