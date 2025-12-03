from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "Ya existe un usuario con este email.",
        },
    )

    OPCIONES_ROL = [
        ("admin_veterinaria", "Administrador Veterinaria"),
        ("veterinario", "Veterinario"),
        ("cliente", "Cliente"),
    ]

    rol = models.CharField(max_length=20, choices=OPCIONES_ROL, default="cliente")
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    dni = models.CharField(max_length=10, unique=True, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # Relación directa con clínica (para todos los roles)
    clinica = models.ForeignKey(
        "clinicas.Clinica",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    # Estados de usuario
    pendiente_aprobacion = models.BooleanField(default=False)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Configurar email como campo de autenticación
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        nombre_completo = self.get_full_name()
        rol_display = self.get_rol_display()

        if nombre_completo.strip():
            return f"{nombre_completo} ({rol_display})"
        elif self.email:
            return f"{self.email} ({rol_display})"
        else:
            return f"{self.username} ({rol_display})"

    @property
    def is_admin_veterinaria(self):
        return self.rol == "admin_veterinaria"

    @property
    def is_veterinario(self):
        return self.rol == "veterinario"

    @property
    def is_cliente(self):
        return self.rol == "cliente"

    @property
    def dashboard_url(self):
        if self.rol == "veterinario":
            return reverse("core:dashboard_veterinario")
        elif self.rol == "cliente":
            return reverse("core:dashboard_cliente")
        elif self.rol == "admin_veterinaria":
            return reverse("core:dashboard_admin")
        return reverse("core:home")


class PerfilVeterinario(models.Model):
    """Información específica del veterinario"""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100, blank=True)
    experiencia_anos = models.PositiveIntegerField(default=0)

    # NUEVOS CAMPOS DE CONFIGURACIÓN
    duracion_turno_default = models.IntegerField(
        default=30, help_text="Duración en minutos"
    )
    telefono_profesional = models.CharField(max_length=20, blank=True)

    # Para el PDF
    firma_digital = models.ImageField(upload_to="firmas/", blank=True, null=True)

    # Preferencias
    recibir_emails_reservas = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr/a. {self.user.get_full_name()} - {self.matricula}"


class PerfilCliente(models.Model):
    """Información específica del cliente"""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    contacto_emergencia = models.CharField(max_length=100, blank=True)
    telefono_emergencia = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Cliente: {self.user.get_full_name()}"


# Señales para crear perfiles automáticamente
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea perfiles automáticamente cuando se crea un usuario.
    Para veterinarios creados desde el formulario admin, NO crear perfil aquí.
    """
    if created:
        if (
            hasattr(instance, "_skip_perfil_creation")
            and instance._skip_perfil_creation
        ):
            return

        if instance.rol == "cliente":
            PerfilCliente.objects.create(user=instance)
        elif instance.rol == "veterinario":
            pass


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.rol == "veterinario" and hasattr(instance, "perfilveterinario"):
        instance.perfilveterinario.save()
    elif instance.rol == "cliente" and hasattr(instance, "perfilcliente"):
        instance.perfilcliente.save()
