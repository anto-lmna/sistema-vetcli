from django.urls import path
from .views import (
    home_view,
    dashboard_view,
    dashboard_admin_view,
    dashboard_cliente_view,
    dashboard_veterinario_view,
    PerfilClienteView,
    PerfilClienteUpdateView,
)

app_name = "core"

urlpatterns = [
    path("", home_view, name="home"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/admin/", dashboard_admin_view, name="dashboard_admin"),
    path(
        "dashboard/veterinario/",
        dashboard_veterinario_view,
        name="dashboard_veterinario",
    ),
    path("dashboard/cliente/", dashboard_cliente_view, name="dashboard_cliente"),
    path("mi-perfil/", PerfilClienteView.as_view(), name="perfil_cliente"),
    path(
        "perfil/editar/",
        PerfilClienteUpdateView.as_view(),
        name="editar_perfil_cliente",
    ),
]
