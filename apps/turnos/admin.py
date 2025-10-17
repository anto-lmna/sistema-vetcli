from django.contrib import admin
from .models import EstadoTurno, DisponibilidadVeterinario, Turno


# Estados de Turno
@admin.register(EstadoTurno)
class EstadoTurnoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "codigo", "color", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre", "codigo"]
    ordering = ["nombre"]

    fieldsets = ((None, {"fields": ("nombre", "codigo", "color", "activo")}),)


# Disponibilidad Veterinario
@admin.register(DisponibilidadVeterinario)
class DisponibilidadVeterinarioAdmin(admin.ModelAdmin):
    list_display = [
        "veterinario",
        "clinica",
        "fecha_inicio",
        "fecha_fin",
        "hora_inicio",
        "hora_fin",
        "duracion_turno",
    ]
    list_filter = ["clinica", "veterinario", "fecha_inicio", "fecha_fin"]
    search_fields = ["veterinario__nombre_completo", "veterinario__email"]
    date_hierarchy = "fecha_inicio"
    ordering = ["-fecha_inicio", "hora_inicio"]

    fieldsets = (
        ("Veterinario", {"fields": ("veterinario", "clinica")}),
        (
            "Rango de Fechas",
            {"fields": ("fecha_inicio", "fecha_fin")},
        ),
        (
            "Horario",
            {"fields": ("hora_inicio", "hora_fin", "duracion_turno")},
        ),
    )

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return super().get_queryset(request).select_related("veterinario", "clinica")

    def save_model(self, request, obj, form, change):
        """Generar turnos automáticamente al guardar"""
        super().save_model(request, obj, form, change)
        if not change:  # Solo al crear, no al editar
            obj.generar_turnos_rango()


# Administrar Turnos
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "fecha",
        "hora_inicio",
        "veterinario",
        "get_cliente_nombre",
        "get_mascota_nombre",
        "estado",
        "reservado",
        "tipo_consulta",
    ]
    list_filter = [
        "clinica",
        "veterinario",
        "estado",
        "reservado",
        "fecha",
        "tipo_consulta",
    ]
    search_fields = [
        "mascota__nombre",
        "cliente__nombre_completo",
        "cliente__email",
        "veterinario__nombre_completo",
        "motivo",
    ]
    date_hierarchy = "fecha"
    ordering = ["-fecha", "hora_inicio"]
    readonly_fields = ["fecha_creacion", "hora_fin"]

    fieldsets = (
        (
            "📋 Información General",
            {"fields": ("clinica", "veterinario", "estado", "reservado")},
        ),
        (
            "👤 Cliente y Mascota",
            {
                "fields": ("cliente", "mascota"),
                "description": "Solo se llenan cuando el turno es reservado",
            },
        ),
        (
            "🕐 Fecha y Horario",
            {"fields": ("fecha", "hora_inicio", "hora_fin", "duracion_minutos")},
        ),
        ("📝 Detalles de la Consulta", {"fields": ("tipo_consulta", "motivo")}),
        (
            "🔍 Metadatos",
            {"fields": ("creado_por", "fecha_creacion"), "classes": ("collapse",)},
        ),
    )

    def get_cliente_nombre(self, obj):
        """Muestra el nombre del cliente o 'Disponible'"""
        return obj.cliente.nombre_completo if obj.cliente else "Disponible"

    get_cliente_nombre.short_description = "Cliente"
    get_cliente_nombre.admin_order_field = "cliente__nombre_completo"

    def get_mascota_nombre(self, obj):
        """Muestra el nombre de la mascota o '-'"""
        return obj.mascota.nombre if obj.mascota else "-"

    get_mascota_nombre.short_description = "Mascota"
    get_mascota_nombre.admin_order_field = "mascota__nombre"

    def get_queryset(self, request):
        """Optimizar consultas con select_related"""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "cliente", "veterinario", "mascota", "estado", "clinica", "creado_por"
            )
        )

    def get_readonly_fields(self, request, obj=None):
        """Bloquear campos en edición"""
        readonly = list(self.readonly_fields)

        if obj:  # Si está editando
            # No permitir cambiar veterinario, fecha ni horario
            readonly.extend(
                ["veterinario", "fecha", "hora_inicio", "duracion_minutos", "clinica"]
            )

            # Si ya está reservado, no permitir modificar cliente/mascota
            if obj.reservado:
                readonly.extend(["cliente", "mascota"])

        return readonly

    def has_delete_permission(self, request, obj=None):
        """Evitar eliminar turnos reservados"""
        if obj and obj.reservado:
            return False
        return super().has_delete_permission(request, obj)

    # Acciones personalizadas
    actions = ["marcar_como_completado", "marcar_como_no_asistio"]

    def marcar_como_completado(self, request, queryset):
        """Marca turnos seleccionados como completados"""
        estado_completado = EstadoTurno.objects.get(codigo=EstadoTurno.COMPLETADO)
        count = queryset.filter(reservado=True).update(estado=estado_completado)
        self.message_user(request, f"{count} turno(s) marcado(s) como completado.")

    marcar_como_completado.short_description = "✅ Marcar como completado"

    def marcar_como_no_asistio(self, request, queryset):
        """Marca turnos como 'no asistió'"""
        estado_no_asistio = EstadoTurno.objects.get(codigo=EstadoTurno.NO_ASISTIO)
        count = queryset.filter(reservado=True).update(estado=estado_no_asistio)
        self.message_user(request, f"{count} turno(s) marcado(s) como 'No asistió'.")

    marcar_como_no_asistio.short_description = "❌ Marcar como 'No asistió'"
