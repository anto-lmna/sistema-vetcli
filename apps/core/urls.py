from django.urls import path
from .views import (
    HomeView,
    DashboardView,
    DashboardAdminView,
    DashboardVeterinarioView,
    DashboardClienteView,
    PerfilClienteView,
    PerfilClienteUpdateView,
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
    path("perfil/cliente/", PerfilClienteView.as_view(), name="perfil_cliente"),
    path(
        "perfil/cliente/editar/",
        PerfilClienteUpdateView.as_view(),
        name="editar_perfil_cliente",
    ),
]
