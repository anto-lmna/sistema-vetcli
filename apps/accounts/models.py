from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("admin_veterinaria", "Administrador Veterinaria"),
        ("veterinario", "Veterinario"),
        ("cliente", "Cliente"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="cliente")
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    dni = models.CharField(max_length=10, unique=True, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    is_active_user = models.BooleanField(default=True)  # Para inactivar usuarios

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin_veterinaria(self):
        return self.role == "admin_veterinaria"

    @property
    def is_veterinario(self):
        return self.role == "veterinario"

    @property
    def is_cliente(self):
        return self.role == "cliente"


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
    ocupacion = models.CharField(max_length=100, blank=True)
    contacto_emergencia = models.CharField(max_length=100, blank=True)
    telefono_emergencia = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Cliente: {self.user.get_full_name()}"


# Señales para crear perfiles automáticamente
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "veterinario":
            PerfilVeterinario.objects.create(user=instance)
        elif instance.role == "cliente":
            PerfilCliente.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == "veterinario" and hasattr(instance, "perfilvet"):
        instance.perfilveterinario.save()
    elif instance.role == "cliente" and hasattr(instance, "perfilcliente"):
        instance.perfilcliente.save()
