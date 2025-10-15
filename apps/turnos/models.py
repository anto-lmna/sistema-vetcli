from django.db import models
from apps.accounts.models import CustomUser
from apps.clinicas.models import Clinica
from apps.mascotas.models import Mascota


class EstadoTurno(models.Model):
    """Estados posibles de un turno"""

    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    EN_CURSO = "en_curso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"
    NO_ASISTIO = "no_asistio"

    CODIGO_CHOICES = [
        (PENDIENTE, "Pendiente"),
        (CONFIRMADO, "Confirmado"),
        (EN_CURSO, "En curso"),
        (COMPLETADO, "Completado"),
        (CANCELADO, "Cancelado"),
        (NO_ASISTIO, "No asistió"),
    ]

    nombre = models.CharField(max_length=50, unique=True)
    codigo = models.CharField(max_length=20, choices=CODIGO_CHOICES, unique=True)
    color = models.CharField(max_length=7, default="#6c757d")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class DisponibilidadVeterinario(models.Model):
    """Bloques de tiempo en los que el veterinario está disponible"""

    veterinario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"rol": "veterinario"},
        related_name="disponibilidades",
    )
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_turno = models.PositiveIntegerField(
        default=30, help_text="Duración en minutos"
    )

    class Meta:
        verbose_name = "Disponibilidad del Veterinario"
        verbose_name_plural = "Disponibilidades de Veterinarios"
        ordering = ["fecha", "hora_inicio"]

    def __str__(self):
        return f"{self.veterinario} - {self.fecha} ({self.hora_inicio}-{self.hora_fin})"

    def generar_turnos(self):
        """Divide el bloque horario en turnos individuales (pendientes)"""
        from datetime import datetime, timedelta

        estado_pendiente = EstadoTurno.objects.get(codigo=EstadoTurno.PENDIENTE)

        hora_actual = datetime.combine(self.fecha, self.hora_inicio)
        hora_fin_dt = datetime.combine(self.fecha, self.hora_fin)

        while hora_actual < hora_fin_dt:
            Turno.objects.get_or_create(
                clinica=self.clinica,
                veterinario=self.veterinario,
                fecha=self.fecha,
                hora_inicio=hora_actual.time(),
                defaults={
                    "estado": estado_pendiente,
                    "duracion_minutos": self.duracion_turno,
                    "creado_por": self.veterinario,
                },
            )
            hora_actual += timedelta(minutes=self.duracion_turno)


class Turno(models.Model):
    """Turno disponible o reservado"""

    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"rol": "veterinario"},
        related_name="turnos_vet",
    )
    cliente = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"rol": "cliente"},
        related_name="turnos_cliente",
    )
    mascota = models.ForeignKey(
        Mascota, on_delete=models.SET_NULL, null=True, blank=True
    )

    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField(null=True, blank=True)
    duracion_minutos = models.PositiveIntegerField(default=30)
    tipo_consulta = models.CharField(max_length=50, default="consulta")
    motivo = models.TextField(blank=True)
    estado = models.ForeignKey(EstadoTurno, on_delete=models.PROTECT)
    reservado = models.BooleanField(default=False)
    creado_por = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha", "hora_inicio"]
        unique_together = [["veterinario", "fecha", "hora_inicio"]]

    def __str__(self):
        return f"{self.veterinario} - {self.fecha} {self.hora_inicio}"

    def save(self, *args, **kwargs):
        if not self.hora_fin and self.hora_inicio:
            from datetime import datetime, timedelta

            hora_dt = datetime.combine(self.fecha, self.hora_inicio)
            self.hora_fin = (hora_dt + timedelta(minutes=self.duracion_minutos)).time()
        super().save(*args, **kwargs)

    def reservar(self, cliente, mascota):
        """Reserva un turno disponible"""
        if self.reservado:
            raise ValueError("El turno ya está reservado.")
        self.cliente = cliente
        self.mascota = mascota
        self.reservado = True
        self.estado = EstadoTurno.objects.get(codigo=EstadoTurno.CONFIRMADO)
        self.save()
