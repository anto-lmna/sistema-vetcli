# apps/clinicas/models.py
from django.db import models
from django.conf import settings


class Clinica(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    email = models.EmailField()

    # Relación con el administrador
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "admin_veterinaria"},
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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clínica"
        verbose_name_plural = "Clínicas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def veterinarios(self):
        """Retorna todos los veterinarios asociados a esta clínica"""
        from apps.accounts.models import PerfilVeterinario

        return PerfilVeterinario.objects.filter(clinica=self)

    @property
    def total_veterinarios(self):
        return self.veterinarios.count()


class HorarioEspecial(models.Model):
    """Para manejar horarios especiales o días de cierre"""

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
