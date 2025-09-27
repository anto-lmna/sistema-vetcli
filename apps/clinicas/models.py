from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Clinica(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    email = models.EmailField()

    # Relación con el administrador
    admin = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"rol": "admin_veterinaria"},
        related_name="clinica_admin",
    )

    # Horarios de atención
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()

    # Días de atención (JSON field para flexibilidad)
    dias_atencion = models.JSONField(
        default=list, help_text="Lista de días: ['lunes', 'martes', ...]"
    )

    # Estado
    is_active = models.BooleanField(default=True)
    acepta_nuevos_clientes = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Para generar la URL de la Clinica
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL amigable para cada clinica",
    )

    class Meta:
        verbose_name = "Clínica"
        verbose_name_plural = "Clínicas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """URL principal de la clínica"""
        return f"/clinicas/{self.slug}/"

    def get_registro_url(self):
        """URL de pre-registro para clientes"""
        return f"/accounts/pre-registro/{self.slug}/"

    @property
    def veterinarios(self):
        """Retorna todos los veterinarios asociados a esta clínica"""
        from apps.accounts.models import CustomUser

        return CustomUser.objects.filter(rol="veterinario", clinica=self)

    @property
    def total_veterinarios(self):
        return self.veterinarios.count()

    def clientes_pendientes(self):
        """Clientes pre-registrados pendientes de activación"""
        from apps.accounts.models import CustomUser

        return CustomUser.objects.filter(
            clinica=self, rol="cliente", pendiente_aprobacion=True, is_active=False
        )

    def total_clientes_pendientes(self):
        return self.clientes_pendientes().count()


class HorarioEspecial(models.Model):
    """Manejar horarios especiales o días de cierre"""

    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    fecha = models.DateField()
    cerrado = models.BooleanField(default=False)
    hora_apertura_especial = models.TimeField(null=True, blank=True)
    hora_cierre_especial = models.TimeField(null=True, blank=True)
    motivo = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Horario Especial"
        verbose_name_plural = "Horarios Especiales"
        unique_together = ["clinica", "fecha"]

    def __str__(self):
        return f"{self.clinica.nombre} - {self.fecha}"
