from django.contrib import admin
from .models import Especie, Raza, Mascota


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Raza)
class RazaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "especie", "activo"]
    list_filter = ["especie", "activo"]
    search_fields = ["nombre", "especie__nombre"]


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "especie",
        "raza",
        "dueno",
        "sexo",
        "edad_texto",
        "activo",
    ]
    list_filter = ["especie", "sexo", "activo", "esterilizado"]
    search_fields = ["nombre", "dueno__nombre_completo", "numero_chip"]
    readonly_fields = ["fecha_registro", "fecha_modificacion", "edad_texto"]

    fieldsets = (
        (
            "Información Básica",
            {"fields": ("nombre", "especie", "raza", "dueno", "sexo")},
        ),
        (
            "Características Físicas",
            {"fields": ("fecha_nacimiento", "color", "peso", "foto")},
        ),
        ("Identificación", {"fields": ("numero_chip",)}),
        (
            "Información Médica",
            {
                "fields": (
                    "esterilizado",
                    "alergias",
                    "condiciones_preexistentes",
                    "observaciones",
                )
            },
        ),
        ("Estado", {"fields": ("activo", "fecha_fallecimiento")}),
        (
            "Metadatos",
            {
                "fields": ("fecha_registro", "fecha_modificacion"),
                "classes": ("collapse",),
            },
        ),
    )
