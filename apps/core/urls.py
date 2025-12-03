from django.urls import path
from .views import (
    HomeView,
    DashboardView,
    DashboardAdminView,
    DashboardVeterinarioView,
    DashboardClienteView,
    PerfilClienteView,
    PerfilClienteUpdateView,
    AprobarClienteView,
    RechazarClienteView,
    VeterinarioCreateView,
    ListaClientesView,
    ListaVeterinariosView,
    ConfiguracionVeterinarioView,
)

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard/admin/", DashboardAdminView.as_view(), name="dashboard_admin"),
    path(
        "dashboard/veterinario/",
        DashboardVeterinarioView.as_view(),
        name="dashboard_veterinario",
    ),
    path(
        "dashboard/cliente/", DashboardClienteView.as_view(), name="dashboard_cliente"
    ),
    path("clientes/", ListaClientesView.as_view(), name="lista_clientes"),
    path("veterinarios/", ListaVeterinariosView.as_view(), name="lista_veterinarios"),
    # Perfil Cliente
    path("perfil/cliente/", PerfilClienteView.as_view(), name="perfil_cliente"),
    path(
        "perfil/cliente/editar/",
        PerfilClienteUpdateView.as_view(),
        name="editar_perfil_cliente",
    ),
    # Gestión de clientes pendientes
    path(
        "cliente/aprobar/<int:cliente_id>/",
        AprobarClienteView.as_view(),
        name="aprobar_cliente",
    ),
    path(
        "cliente/rechazar/<int:cliente_id>/",
        RechazarClienteView.as_view(),
        name="rechazar_cliente",
    ),
    # Crear Veterinario
    path(
        "veterinarios/crear/", VeterinarioCreateView.as_view(), name="crear_veterinario"
    ),
    path(
        "veterinario/configuracion/",
        ConfiguracionVeterinarioView.as_view(),
        name="configuracion_veterinario",
    ),
]
