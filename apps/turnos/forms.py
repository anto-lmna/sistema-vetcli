from time import timezone
from django import forms
from django.utils import timezone

from apps.accounts.models import CustomUser
from .models import Turno


class TurnoCrearAdminForm(forms.ModelForm):
    """Formulario simplificado para crear turnos como admin"""

    class Meta:
        model = Turno
        fields = [
            "veterinario",
            "fecha",
            "hora_inicio",
            "duracion_minutos",
            "motivo",
        ]
        widgets = {
            "veterinario": forms.Select(attrs={"class": "form-select"}),
            "fecha": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "min": timezone.now().date().isoformat(),
                }
            ),
            "hora_inicio": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "duracion_minutos": forms.NumberInput(
                attrs={"class": "form-control", "min": 15, "max": 120, "value": 30}
            ),
            "motivo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe el motivo de la consulta...",
                }
            ),
        }

    cliente_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    mascota_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["veterinario"].queryset = CustomUser.objects.filter(
                rol="veterinario", clinica=user.clinica, is_active=True
            )
