from django.db import models
from django.core.validators import MinValueValidator
from apps.accounts.models import CustomUser
from django.utils import timezone


class Especie(models.Model):
    """Modelo para especies de animales (Perro, Gato)"""

    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Especie"
        verbose_name_plural = "Especies"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Raza(models.Model):
    """Modelo para razas de animales"""

    nombre = models.CharField(max_length=100)
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name="razas")
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Raza"
        verbose_name_plural = "Razas"
        ordering = ["especie", "nombre"]
        unique_together = ["nombre", "especie"]

    def __str__(self):
        return f"{self.nombre} ({self.especie.nombre})"


class Mascota(models.Model):
    """Modelo principal para mascotas"""

    SEXO_CHOICES = [
        ("M", "Macho"),
        ("H", "Hembra"),
    ]

    # Información básica
    nombre = models.CharField(max_length=100)
    especie = models.ForeignKey(
        Especie, on_delete=models.PROTECT, related_name="mascotas"
    )
    raza = models.ForeignKey(
        Raza, on_delete=models.SET_NULL, null=True, blank=True, related_name="mascotas"
    )

    # Dueño
    dueno = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="mascotas",
        limit_choices_to={"rol": "cliente"},
    )

    # Características físicas
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    fecha_nacimiento = models.DateField(
        null=True, blank=True, help_text="Fecha aproximada de nacimiento"
    )
    color = models.CharField(max_length=100, blank=True)
    peso = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        null=True,
        blank=True,
        help_text="Peso en kilogramos",
    )

    # Identificación
    numero_chip = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
        help_text="Número de microchip",
    )
    foto = models.ImageField(upload_to="mascotas/fotos/", blank=True, null=True)

    # Información médica básica
    esterilizado = models.BooleanField(
        default=False, help_text="¿Está castrado/esterilizado?"
    )
    alergias = models.TextField(
        blank=True, help_text="Alergias conocidas (medicamentos, alimentos, etc.)"
    )
    condiciones_preexistentes = models.TextField(
        blank=True, help_text="Condiciones médicas crónicas o importantes"
    )
    observaciones = models.TextField(
        blank=True, help_text="Observaciones generales sobre la mascota"
    )

    # Control de estado
    activo = models.BooleanField(default=True, help_text="Mascota activa en el sistema")
    fecha_fallecimiento = models.DateField(
        null=True, blank=True, help_text="Fecha de fallecimiento (si aplica)"
    )

    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ["-fecha_registro"]
        indexes = [
            models.Index(fields=["dueno", "activo"]),
            models.Index(fields=["numero_chip"]),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.get_sexo_display()}) - {self.dueno.get_full_name}"

    @property
    def edad(self):
        """Calcula la edad de la mascota en años"""
        if not self.fecha_nacimiento:
            return None

        fecha_calculo = self.fecha_fallecimiento or timezone.now().date()
        edad = fecha_calculo.year - self.fecha_nacimiento.year

        # Ajustar si aún no cumplió años este año
        if fecha_calculo.month < self.fecha_nacimiento.month or (
            fecha_calculo.month == self.fecha_nacimiento.month
            and fecha_calculo.day < self.fecha_nacimiento.day
        ):
            edad -= 1

        return edad

    @property
    def edad_texto(self):
        """Retorna la edad en formato legible"""
        edad = self.edad
        if edad is None:
            return "Edad desconocida"

        if edad == 0:
            # Calcular meses para cachorros
            meses = (timezone.now().date() - self.fecha_nacimiento).days // 30
            return f"{meses} meses" if meses != 1 else "1 mes"

        return f"{edad} años" if edad != 1 else "1 año"

    @property
    def esta_fallecido(self):
        """Verifica si la mascota ha fallecido"""
        return self.fecha_fallecimiento is not None

    def inactivar(self, fecha_fallecimiento=None):
        """Inactiva la mascota (método usado por admin)"""
        self.activo = False
        if fecha_fallecimiento:
            self.fecha_fallecimiento = fecha_fallecimiento
        self.save()

    def activar(self):
        """Reactiva la mascota"""
        self.activo = True
        self.fecha_fallecimiento = None
        self.save()

    def save(self, *args, **kwargs):
        # Si tiene fecha de fallecimiento,tiene que estar inactiva
        if self.fecha_fallecimiento:
            self.activo = False

        # Limpiar numero_chip si está vacío (para evitar problemas con unique)
        if self.numero_chip == "":
            self.numero_chip = None

        super().save(*args, **kwargs)
