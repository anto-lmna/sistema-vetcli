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

    # Estados de usuario
    is_active_user = models.BooleanField(default=True)  # Para inactivar usuarios
    pendiente_aprobacion = models.BooleanField(
        default=False
    )  # Para clientes pre-registrados
    fecha_aprobacion = models.DateTimeField(
        null=True, blank=True
    )  # Cuándo fue aprobado
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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100, blank=True)
    experiencia_anos = models.PositiveIntegerField(default=0)
    clinica = models.ForeignKey(
        "clinicas.Clinica", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Dr/a. {self.user.get_full_name()} - {self.matricula}"


class PerfilCliente(models.Model):
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
    if instance.rol == "veterinario" and hasattr(instance, "perfilvet"):
        instance.perfilveterinario.save()
    elif instance.rol == "cliente" and hasattr(instance, "perfilcliente"):
        instance.perfilcliente.save()
