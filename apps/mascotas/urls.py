from django.urls import path
from . import views

app_name = "mascotas"

urlpatterns = [
    # URLs para CLIENTES
    path("mis-mascotas/", views.mis_mascotas, name="mis_mascotas"),
    path("agregar/", views.agregar_mascota, name="agregar_mascota"),
    path("editar/<int:pk>/", views.editar_mascota, name="editar_mascota"),
    path("detalle/<int:pk>/", views.detalle_mascota, name="detalle_mascota"),
    # URLs para ADMIN
    path("admin/lista/", views.lista_mascotas_admin, name="lista_mascotas_admin"),
    path("admin/crear/", views.crear_mascota_admin, name="crear_mascota_admin"),
    path(
        "admin/editar/<int:pk>/",
        views.editar_mascota_admin,
        name="editar_mascota_admin",
    ),
    path(
        "admin/inactivar/<int:pk>/", views.inactivar_mascota, name="inactivar_mascota"
    ),
    path("admin/activar/<int:pk>/", views.activar_mascota, name="activar_mascota"),
    # URLs para VETERINARIOS
    path(
        "veterinario/lista/",
        views.lista_mascotas_veterinario,
        name="lista_mascotas_veterinario",
    ),
    # AJAX
    path("ajax/cargar-razas/", views.cargar_razas, name="cargar_razas"),
]
