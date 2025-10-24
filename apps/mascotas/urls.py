from django.urls import path
from .views import (
    # Vistas de Cliente
    MisMascotasListView,
    AgregarMascotaView,
    EditarMascotaView,
    DetalleMascotaView,
    # Vistas de Admin
    ListaMascotasAdminView,
    CrearMascotaAdminView,
    EditarMascotaAdminView,
    InactivarMascotaView,
    ActivarMascotaView,
    # Vistas de Veterinario
    ListaMascotasVeterinarioView,
    # AJAX
    CargarRazasView,
)

app_name = "mascotas"

urlpatterns = [
    # Cliente
    path("mis-mascotas/", MisMascotasListView.as_view(), name="mis_mascotas"),
    path("agregar/", AgregarMascotaView.as_view(), name="agregar_mascota"),
    path("editar/<int:pk>/", EditarMascotaView.as_view(), name="editar_mascota"),
    path("detalle/<int:pk>/", DetalleMascotaView.as_view(), name="detalle_mascota"),
    # Admin
    path("admin/lista/", ListaMascotasAdminView.as_view(), name="lista_mascotas_admin"),
    path("admin/crear/", CrearMascotaAdminView.as_view(), name="crear_mascota_admin"),
    path(
        "admin/editar/<int:pk>/",
        EditarMascotaAdminView.as_view(),
        name="editar_mascota_admin",
    ),
    path(
        "admin/inactivar/<int:pk>/",
        InactivarMascotaView.as_view(),
        name="inactivar_mascota",
    ),
    path(
        "admin/activar/<int:pk>/", ActivarMascotaView.as_view(), name="activar_mascota"
    ),
    # Veterinario
    path(
        "veterinario/lista/",
        ListaMascotasVeterinarioView.as_view(),
        name="lista_mascotas_veterinario",
    ),
    # AJAX
    path("ajax/cargar-razas/", CargarRazasView.as_view(), name="cargar_razas"),
]
