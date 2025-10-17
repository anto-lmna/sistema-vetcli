from django.db import models
from datetime import datetime, timedelta

from django.forms import ValidationError
from apps.accounts.models import CustomUser
from apps.clinicas.models import Clinica
from apps.mascotas.models import Mascota


# class EstadoTurno(models.Model):
#     """Estados posibles de un turno"""

#     PENDIENTE = "pendiente"
#     CONFIRMADO = "confirmado"
#     EN_CURSO = "en_curso"
#     COMPLETADO = "completado"
#     CANCELADO = "cancelado"
#     NO_ASISTIO = "no_asistio"

#     CODIGO_CHOICES = [
#         (PENDIENTE, "Pendiente"),
#         (CONFIRMADO, "Confirmado"),
#         (EN_CURSO, "En curso"),
#         (COMPLETADO, "Completado"),
#         (CANCELADO, "Cancelado"),
#         (NO_ASISTIO, "No asistió"),
#     ]

#     nombre = models.CharField(max_length=50, unique=True)
#     codigo = models.CharField(max_length=20, choices=CODIGO_CHOICES, unique=True)
#     color = models.CharField(max_length=7, default="#6c757d")
#     activo = models.BooleanField(default=True)

#     def __str__(self):
#         return self.nombre


# class DisponibilidadVeterinario(models.Model):
#     """Bloques de tiempo en los que el veterinario está disponible"""

#     veterinario = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         limit_choices_to={"rol": "veterinario"},
#         related_name="disponibilidades",
#     )
#     clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
#     fecha_inicio = models.DateField(null=True, blank=True)
#     fecha_fin = models.DateField(null=True, blank=True)
#     hora_inicio = models.TimeField()
#     hora_fin = models.TimeField()
#     duracion_turno = models.PositiveIntegerField(
#         default=30, help_text="Duración en minutos"
#     )

#     class Meta:
#         verbose_name = "Disponibilidad del Veterinario"
#         verbose_name_plural = "Disponibilidades de Veterinarios"
#         ordering = ["-fecha_inicio", "hora_inicio"]

#     def __str__(self):
#         return f"{self.veterinario} | {self.fecha_inicio} → {self.fecha_fin} ({self.hora_inicio}-{self.hora_fin})"

#     @property
#     def turnos_generados(self):
#         """Devuelve los turnos generados dentro del rango de esta disponibilidad"""
#         return Turno.objects.filter(
#             veterinario=self.veterinario,
#             clinica=self.clinica,
#             fecha__range=(self.fecha_inicio, self.fecha_fin),
#             hora_inicio__gte=self.hora_inicio,
#             hora_fin__lte=self.hora_fin,
#         )

#     @property
#     def turnos_reservados(self):
#         """Devuelve solo los turnos reservados en este rango"""
#         return self.turnos_generados.filter(reservado=True)

#     # === Lógica principal de generación ===
#     def generar_turnos_rango(self):
#         """Genera turnos desde fecha_inicio hasta fecha_fin (inclusive)"""

#         estado_pendiente = EstadoTurno.objects.get(codigo=EstadoTurno.PENDIENTE)
#         fecha_actual = self.fecha_inicio

#         while fecha_actual <= self.fecha_fin:
#             dia_semana = fecha_actual.strftime("%A").lower()
#             # Solo generar si la clínica atiende ese día (si existe esa lista)
#             if (
#                 hasattr(self.clinica, "dias_atencion")
#                 and dia_semana in self.clinica.dias_atencion
#             ):
#                 hora_actual = datetime.combine(fecha_actual, self.hora_inicio)
#                 hora_fin_dt = datetime.combine(fecha_actual, self.hora_fin)

#                 while hora_actual < hora_fin_dt:
#                     Turno.objects.get_or_create(
#                         clinica=self.clinica,
#                         veterinario=self.veterinario,
#                         fecha=fecha_actual,
#                         hora_inicio=hora_actual.time(),
#                         defaults={
#                             "estado": estado_pendiente,
#                             "duracion_minutos": self.duracion_turno,
#                             "creado_por": self.veterinario,
#                         },
#                     )
#                     hora_actual += timedelta(minutes=self.duracion_turno)

#             fecha_actual += timedelta(days=1)


# class Turno(models.Model):
#     """Turno disponible o reservado"""

#     clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
#     veterinario = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         limit_choices_to={"rol": "veterinario"},
#         related_name="turnos_vet",
#     )
#     cliente = models.ForeignKey(
#         CustomUser,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         limit_choices_to={"rol": "cliente"},
#         related_name="turnos_cliente",
#     )
#     mascota = models.ForeignKey(
#         Mascota, on_delete=models.SET_NULL, null=True, blank=True
#     )

#     fecha = models.DateField()
#     hora_inicio = models.TimeField()
#     hora_fin = models.TimeField(null=True, blank=True)
#     duracion_minutos = models.PositiveIntegerField(default=30)
#     tipo_consulta = models.CharField(max_length=50, default="consulta")
#     motivo = models.TextField(blank=True)
#     estado = models.ForeignKey(EstadoTurno, on_delete=models.PROTECT)
#     reservado = models.BooleanField(default=False)
#     creado_por = models.ForeignKey(
#         CustomUser, on_delete=models.SET_NULL, null=True, related_name="+"
#     )
#     fecha_creacion = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["fecha", "hora_inicio"]
#         unique_together = [["veterinario", "fecha", "hora_inicio"]]

#     def __str__(self):
#         return f"{self.veterinario} - {self.fecha} {self.hora_inicio}"

#     def save(self, *args, **kwargs):
#         if not self.hora_fin and self.hora_inicio:
#             from datetime import datetime, timedelta

#             hora_dt = datetime.combine(self.fecha, self.hora_inicio)
#             self.hora_fin = (hora_dt + timedelta(minutes=self.duracion_minutos)).time()
#         super().save(*args, **kwargs)

#     def reservar(self, cliente, mascota):
#         """Reserva un turno disponible"""
#         if self.reservado:
#             raise ValueError("El turno ya está reservado.")
#         self.cliente = cliente
#         self.mascota = mascota
#         self.reservado = True
#         self.estado = EstadoTurno.objects.get(codigo=EstadoTurno.CONFIRMADO)
#         self.save()


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
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_turno = models.PositiveIntegerField(
        default=30, help_text="Duración en minutos"
    )

    class Meta:
        verbose_name = "Disponibilidad del Veterinario"
        verbose_name_plural = "Disponibilidades de Veterinarios"
        ordering = ["-fecha_inicio", "hora_inicio"]

    def __str__(self):
        return f"{self.veterinario} | {self.fecha_inicio} → {self.fecha_fin} ({self.hora_inicio}-{self.hora_fin})"

    @property
    def turnos_generados(self):
        """Devuelve los turnos generados dentro del rango de esta disponibilidad"""
        return Turno.objects.filter(
            veterinario=self.veterinario,
            clinica=self.clinica,
            fecha__range=(self.fecha_inicio, self.fecha_fin),
            hora_inicio__lt=self.hora_fin,
            hora_fin__gt=self.hora_inicio,
        )

    @property
    def turnos_reservados(self):
        """Devuelve solo los turnos reservados en este rango"""
        return self.turnos_generados.filter(reservado=True)

    def generar_turnos_rango(self):
        """
        Genera turnos desde fecha_inicio hasta fecha_fin respetando:
        - Duración actual del turno.
        - Turnos ya existentes para evitar solapamientos.
        """
        estado_pendiente = EstadoTurno.objects.get(codigo=EstadoTurno.PENDIENTE)
        fecha_actual = self.fecha_inicio

        while fecha_actual <= self.fecha_fin:
            dia_semana = fecha_actual.strftime("%A").lower()
            if (
                hasattr(self.clinica, "dias_atencion")
                and dia_semana in self.clinica.dias_atencion
            ):
                hora_actual = datetime.combine(fecha_actual, self.hora_inicio)
                hora_fin_dt = datetime.combine(fecha_actual, self.hora_fin)

                while (
                    hora_actual + timedelta(minutes=self.duracion_turno) <= hora_fin_dt
                ):
                    nuevo_inicio = hora_actual.time()
                    nuevo_fin = (
                        hora_actual + timedelta(minutes=self.duracion_turno)
                    ).time()

                    # Verificar solapamientos
                    turno_solapado = Turno.objects.filter(
                        veterinario=self.veterinario,
                        clinica=self.clinica,
                        fecha=fecha_actual,
                        hora_inicio__lt=nuevo_fin,
                        hora_fin__gt=nuevo_inicio,
                    ).exists()

                    if not turno_solapado:
                        Turno.objects.create(
                            clinica=self.clinica,
                            veterinario=self.veterinario,
                            fecha=fecha_actual,
                            hora_inicio=nuevo_inicio,
                            hora_fin=nuevo_fin,
                            duracion_minutos=self.duracion_turno,
                            estado=estado_pendiente,
                            creado_por=self.veterinario,
                        )

                    hora_actual += timedelta(minutes=self.duracion_turno)
            fecha_actual += timedelta(days=1)

    def clean(self):
        # Validaciones básicas
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError(
                "La hora de inicio debe ser menor que la hora de fin."
            )
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError(
                "La fecha de inicio no puede ser mayor que la fecha de fin."
            )

    @property
    def turnos_reservados(self):
        """Devuelve solo los turnos reservados en este rango"""
        return self.turnos_generados.filter(reservado=True)


def generar_turnos_rango(self):
    """
    Genera turnos desde fecha_inicio hasta fecha_fin respetando:
    - Duración actual del turno.
    - Turnos ya existentes para evitar solapamientos.
    """
    estado_pendiente = EstadoTurno.objects.get(codigo=EstadoTurno.PENDIENTE)
    fecha_actual = self.fecha_inicio

    while fecha_actual <= self.fecha_fin:
        dia_semana = fecha_actual.strftime("%A").lower()
        if (
            hasattr(self.clinica, "dias_atencion")
            and dia_semana in self.clinica.dias_atencion
        ):
            hora_actual = datetime.combine(fecha_actual, self.hora_inicio)
            hora_fin_dt = datetime.combine(fecha_actual, self.hora_fin)

            while hora_actual + timedelta(minutes=self.duracion_turno) <= hora_fin_dt:
                nuevo_inicio = hora_actual.time()
                nuevo_fin = (
                    hora_actual + timedelta(minutes=self.duracion_turno)
                ).time()

                # Verificar si existe algún turno que se solape
                turno_solapado = Turno.objects.filter(
                    veterinario=self.veterinario,
                    clinica=self.clinica,
                    fecha=fecha_actual,
                    hora_inicio__lt=nuevo_fin,
                    hora_fin__gt=nuevo_inicio,
                ).exists()

                if not turno_solapado:
                    Turno.objects.create(
                        clinica=self.clinica,
                        veterinario=self.veterinario,
                        fecha=fecha_actual,
                        hora_inicio=nuevo_inicio,
                        hora_fin=nuevo_fin,
                        duracion_minutos=self.duracion_turno,
                        estado=estado_pendiente,
                        creado_por=self.veterinario,
                    )

                hora_actual += timedelta(minutes=self.duracion_turno)
        fecha_actual += timedelta(days=1)


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

    def clean(self):
        # Validar que hora_fin coincida con duracion_minutos
        if self.hora_inicio and self.hora_fin:
            delta = datetime.combine(self.fecha, self.hora_fin) - datetime.combine(
                self.fecha, self.hora_inicio
            )
            if delta.total_seconds() / 60 != self.duracion_minutos:
                raise ValidationError(
                    "La hora_fin no coincide con la duración del turno."
                )
        # Validar que la mascota pertenezca al cliente
        if self.mascota and self.cliente and self.mascota.propietario != self.cliente:
            raise ValidationError("La mascota no pertenece al cliente asignado.")

        # No se pueden reservar turnos pasados
        if (
            self.reservado
            and datetime.combine(self.fecha, self.hora_inicio) < datetime.now()
        ):
            raise ValidationError("No se puede reservar un turno en el pasado.")

    def save(self, *args, **kwargs):
        # Calcular hora_fin si no existe
        if not self.hora_fin and self.hora_inicio:
            self.hora_fin = (
                datetime.combine(self.fecha, self.hora_inicio)
                + timedelta(minutes=self.duracion_minutos)
            ).time()
        super().save(*args, **kwargs)

    def reservar(self, cliente, mascota):
        """Reserva un turno disponible"""
        if self.reservado:
            raise ValueError("El turno ya está reservado.")
        if mascota.dueno != cliente:
            raise ValueError("La mascota no pertenece al cliente.")
        if datetime.combine(self.fecha, self.hora_inicio) < datetime.now():
            raise ValueError("No se puede reservar un turno en el pasado.")

        self.cliente = cliente
        self.mascota = mascota
        self.reservado = True
        self.estado = EstadoTurno.objects.get(codigo=EstadoTurno.CONFIRMADO)
        self.save()
