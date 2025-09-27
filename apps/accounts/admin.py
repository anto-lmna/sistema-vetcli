from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PerfilVeterinario, PerfilCliente


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "rol",
        "clinica",
        "is_active",
        "pendiente_aprobacion",
    )
    list_filter = ("rol", "is_active", "pendiente_aprobacion", "clinica", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name", "dni")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Información Personal",
            {"fields": ("telefono", "direccion", "dni", "fecha_nacimiento")},
        ),
        (
            "Configuración de Rol",
            {
                "fields": (
                    "rol",
                    "clinica",
                    "pendiente_aprobacion",
                    "fecha_aprobacion",
                    "aprobado_por",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Información Adicional",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "rol",
                    "telefono",
                    "dni",
                    "clinica",
                )
            },
        ),
    )


@admin.register(PerfilVeterinario)
class PerfilVeterinarioAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "matricula",
        "especialidad",
        "get_clinica",
        "experiencia_anos",
    )
    list_filter = ("especialidad", "user__clinica")
    search_fields = ("user__first_name", "user__last_name", "matricula")

    def get_clinica(self, obj):
        return obj.user.clinica.nombre if obj.user.clinica else "Sin clínica"

    get_clinica.short_description = "Clínica"


@admin.register(PerfilCliente)
class PerfilClienteAdmin(admin.ModelAdmin):
    list_display = ("user", "get_clinica", "contacto_emergencia", "telefono_emergencia")
    list_filter = ("user__clinica",)
    search_fields = ("user__first_name", "user__last_name", "contacto_emergencia")

    def get_clinica(self, obj):
        return obj.user.clinica.nombre if obj.user.clinica else "Sin clínica"

    get_clinica.short_description = "Clínica"
