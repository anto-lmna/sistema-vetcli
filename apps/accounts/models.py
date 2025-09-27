from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
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

    # Estados de usuario (solo para clientes principalmente)
    pendiente_aprobacion = models.BooleanField(default=False)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    @property
    def is_admin_veterinaria(self):
        return self.rol == "admin_veterinaria"

    @property
    def is_veterinario(self):
        return self.rol == "veterinario"

    @property
    def is_cliente(self):
        return self.rol == "cliente"


class PerfilVeterinario(models.Model):
    """Información específica del veterinario"""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100, blank=True)
    experiencia_anos = models.PositiveIntegerField(default=0)

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
    if created:
        if instance.rol == "veterinario":
            PerfilVeterinario.objects.create(user=instance)
        elif instance.rol == "cliente":
            PerfilCliente.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.rol == "veterinario" and hasattr(instance, "perfilveterinario"):
        instance.perfilveterinario.save()
    elif instance.rol == "cliente" and hasattr(instance, "perfilcliente"):
        instance.perfilcliente.save()
