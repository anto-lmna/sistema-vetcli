# turnos/urls.py
from django.urls import path
from .views import (
    # Veterinario - Disponibilidad
    DisponibilidadListView,
    DisponibilidadCreateView,
    DisponibilidadDeleteView,
    # Veterinario - Agenda
    AgendaVeterinarioView,
    TurnoDetalleVeterinarioView,
    TurnoIniciarAtencionView,
    TurnoCompletarView,
    TurnoNoAsistioView,
    TurnosJSONView,
    # Cliente
    TurnosDisponiblesListView,
    TurnoReservarView,
    MisTurnosListView,
    TurnoDetalleClienteView,
    TurnoCancelarClienteView,
    # Administrador
    AgendaClinicaView,
    TurnoDetalleAdminView,
    TurnoCancelarAdminView,
    TurnoCrearAdminView,
    TurnosClinicaJSONView,
    # APIs
    BuscarClientesAPIView,
    MascotasPorClienteAPIView,
)

app_name = "turnos"

urlpatterns = [
    # ==================== VETERINARIO ====================
    # Disponibilidad
    path(
        "disponibilidades/", DisponibilidadListView.as_view(), name="disponibilidades"
    ),
    path(
        "disponibilidad/crear/",
        DisponibilidadCreateView.as_view(),
        name="crear_disponibilidad",
    ),
    path(
        "disponibilidad/eliminar/<int:pk>/",
        DisponibilidadDeleteView.as_view(),
        name="eliminar_disponibilidad",
    ),
    # Agenda
    path("agenda/", AgendaVeterinarioView.as_view(), name="agenda_vet"),
    path(
        "turno/<int:pk>/detalle/",
        TurnoDetalleVeterinarioView.as_view(),
        name="turno_detalle_vet",
    ),
    path(
        "turno/<int:pk>/iniciar/",
        TurnoIniciarAtencionView.as_view(),
        name="turno_iniciar",
    ),
    path(
        "turno/<int:pk>/completar/",
        TurnoCompletarView.as_view(),
        name="turno_completar",
    ),
    path(
        "turno/<int:pk>/no-asistio/",
        TurnoNoAsistioView.as_view(),
        name="turno_no_asistio",
    ),
    # JSON para calendario
    path("api/turnos-json/", TurnosJSONView.as_view(), name="turnos_json"),
    # ==================== CLIENTE ====================
    path(
        "disponibles/", TurnosDisponiblesListView.as_view(), name="turnos_disponibles"
    ),
    path("reservar/<int:pk>/", TurnoReservarView.as_view(), name="reservar_turno"),
    path("mis-turnos/", MisTurnosListView.as_view(), name="mis_turnos"),
    path(
        "mis-turnos/<int:pk>/",
        TurnoDetalleClienteView.as_view(),
        name="turno_detalle_cliente",
    ),
    path(
        "mis-turnos/<int:pk>/cancelar/",
        TurnoCancelarClienteView.as_view(),
        name="cancelar_turno_cliente",
    ),
    # ==================== ADMINISTRADOR ====================
    path("agenda-clinica/", AgendaClinicaView.as_view(), name="agenda_clinica"),
    path(
        "admin/turno/<int:pk>/",
        TurnoDetalleAdminView.as_view(),
        name="turno_detalle_admin",
    ),
    path(
        "admin/turno/<int:pk>/cancelar/",
        TurnoCancelarAdminView.as_view(),
        name="cancelar_turno_admin",
    ),
    path("admin/turno/crear/", TurnoCrearAdminView.as_view(), name="crear_turno_admin"),
    # JSON para calendario clínica
    path(
        "api/turnos-clinica-json/",
        TurnosClinicaJSONView.as_view(),
        name="turnos_clinica_json",
    ),
    # ==================== APIs ====================
    path(
        "api/buscar-clientes/", BuscarClientesAPIView.as_view(), name="buscar_clientes"
    ),
    path(
        "api/cliente/<int:cliente_id>/mascotas/",
        MascotasPorClienteAPIView.as_view(),
        name="mascotas_por_cliente",
    ),
]
