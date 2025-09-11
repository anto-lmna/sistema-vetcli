from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/admin/", views.dashboard_admin_view, name="dashboard_admin"),
    path(
        "dashboard/veterinario/",
        views.dashboard_veterinario_view,
        name="dashboard_veterinario",
    ),
    path("dashboard/cliente/", views.dashboard_cliente_view, name="dashboard_cliente"),
]
