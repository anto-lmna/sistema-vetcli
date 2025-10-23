from django import forms
from django.utils import timezone
from apps.accounts.models import CustomUser


class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "telefono",
            "direccion",
            "dni",
            "fecha_nacimiento",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "dni": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-control"},
            ),
        }
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "telefono": "Teléfono",
            "direccion": "Dirección",
            "dni": "DNI",
            "fecha_nacimiento": "Fecha de nacimiento",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.fecha_nacimiento:
            self.initial["fecha_nacimiento"] = self.instance.fecha_nacimiento.strftime(
                "%Y-%m-%d"
            )

    def clean_fecha_nacimiento(self):
        """Evita fechas futuras"""
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and fecha > timezone.now().date():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha
