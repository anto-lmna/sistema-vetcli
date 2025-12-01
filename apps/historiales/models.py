# Create your models here.
import os
from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.mascotas.models import Mascota
from apps.turnos.models import Turno
from apps.clinicas.models import Clinica


class HistoriaClinica(models.Model):
    clinica = models.ForeignKey(
        "clinicas.Clinica", on_delete=models.CASCADE, related_name="historias_clinicas"
    )
    mascota = models.ForeignKey(
        "mascotas.Mascota",
        on_delete=models.PROTECT,
        related_name="historial_medico",
    )
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"rol": "veterinario"},
    )

    # Vincular con un Turno específico si existe
    turno = models.OneToOneField(
        "turnos.Turno",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historia_clinica",
    )

    # 2. Datos de la Consulta (Signos Vitales)
    fecha = models.DateTimeField(default=timezone.now)
    motivo_consulta = models.CharField(max_length=255)
    peso_actual = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Peso en KG"
    )
    temperatura = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    frecuencia_cardiaca = models.IntegerField(null=True, blank=True, help_text="LPM")

    # 3. El núcleo médico (Anamnesis y Diagnóstico)
    anamnesis = models.TextField(help_text="Antecedentes y síntomas descritos")
    hallazgos_fisicos = models.TextField(
        blank=True, help_text="Lo que el vet observa en el examen"
    )
    diagnostico = models.TextField()

    # 4. Tratamiento y Notas
    tratamiento_realizado = models.TextField(help_text="Lo que se hizo EN la consulta")
    indicaciones_dueno = models.TextField(help_text="Receta/Instrucciones para casa")

    # Bloquear la edición después de cierto tiempo para integridad legal
    es_borrador = models.BooleanField(default=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Historia Clínica"
        verbose_name_plural = "Historias Clínicas"

    def __str__(self):
        return f"{self.mascota} - {self.fecha.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        # Actualizar el peso en el modelo Mascota automáticamente
        if self.pk is None and self.peso_actual:
            self.mascota.peso = self.peso_actual
            self.mascota.save()
        super().save(*args, **kwargs)


# Modelo Vacuna
class Vacuna(models.Model):
    mascota = models.ForeignKey(
        "mascotas.Mascota", on_delete=models.CASCADE, related_name="vacunas"
    )
    # Vinculamos la vacuna a una visita médica específica
    historia_clinica = models.ForeignKey(
        HistoriaClinica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacunas_aplicadas",
    )
    nombre = models.CharField(max_length=100, help_text="Ej: Quintuple, Antirrábica")
    lote = models.CharField(
        max_length=50, blank=True, help_text="Para trazabilidad en caso de problemas"
    )

    fecha_aplicacion = models.DateField(default=timezone.now)
    fecha_proxima_aplicacion = models.DateField(
        help_text="Fecha para el recordatorio automático"
    )

    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"rol": "veterinario"},
    )

    class Meta:
        ordering = ["-fecha_aplicacion"]
        verbose_name = "Vacuna"
        verbose_name_plural = "Vacunas"

    def __str__(self):
        return f"{self.nombre} - {self.mascota.nombre}"

    @property
    def esta_vencida(self):
        return self.fecha_proxima_aplicacion < timezone.now().date()


# Archivos Adjuntos


def historia_clinica_upload_path(instance, filename):
    # Genera ruta: clinicas/slug_clinica/mascotas/id_mascota/filename
    clinica_slug = instance.historia.clinica.slug
    mascota_id = instance.historia.mascota.id
    return f"clinicas/{clinica_slug}/mascotas/{mascota_id}/historias/{filename}"


class ArchivoAdjunto(models.Model):
    historia = models.ForeignKey(
        HistoriaClinica, on_delete=models.CASCADE, related_name="archivos"
    )
    archivo = models.FileField(upload_to=historia_clinica_upload_path)
    descripcion = models.CharField(
        max_length=100, blank=True, help_text="Ej: Radiografía tórax"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"

    def __str__(self):
        return f"Archivo {self.id} de {self.historia}"

    def extension(self):
        name, extension = os.path.splitext(self.archivo.name)
        return extension.lower()
