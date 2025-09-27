from django.contrib import admin
from .models import Clinica

# Register your models here.
from django.contrib import admin
from .models import Clinica, HorarioEspecial


from django.contrib import admin
from .models import Clinica, HorarioEspecial


@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "get_admin",
        "telefono",
        "email",
        "is_active",
        "acepta_nuevos_clientes",
    )
    list_filter = ("is_active", "acepta_nuevos_clientes", "fecha_creacion")
    search_fields = ("nombre", "email")
    prepopulated_fields = {"slug": ("nombre",)}

    def get_admin(self, obj):
        return obj.admin.get_full_name() if obj.admin else "Sin administrador"

    get_admin.short_description = "Administrador"

    fieldsets = (
        ("Información Básica", {"fields": ("nombre", "descripcion", "slug")}),
        ("Contacto", {"fields": ("direccion", "telefono", "email")}),
        ("Horarios", {"fields": ("hora_apertura", "hora_cierre", "dias_atencion")}),
        ("Estado", {"fields": ("is_active", "acepta_nuevos_clientes")}),
    )


@admin.register(HorarioEspecial)
class HorarioEspecialAdmin(admin.ModelAdmin):
    list_display = ("clinica", "fecha", "cerrado", "motivo")
    list_filter = ("cerrado", "fecha")
    search_fields = ("clinica__nombre", "motivo")
