from django import forms
from django.forms import inlineformset_factory
from .models import HistoriaClinica, Vacuna, ArchivoAdjunto


class EstiloFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Si es un checkbox, usa 'form-check-input'
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            # Para todo lo demás (texto, select, fechas), usa 'form-control'
            else:
                field.widget.attrs["class"] = "form-control"


class HistoriaClinicaForm(EstiloFormMixin, forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        fields = [
            "motivo_consulta",
            "peso_actual",
            "temperatura",
            "frecuencia_cardiaca",
            "anamnesis",
            "hallazgos_fisicos",
            "diagnostico",
            "tratamiento_realizado",
            "indicaciones_dueno",
            "es_borrador",
        ]
        widgets = {
            "anamnesis": forms.Textarea(attrs={"rows": 3}),
            "diagnostico": forms.Textarea(attrs={"rows": 3}),
            "tratamiento_realizado": forms.Textarea(attrs={"rows": 3}),
            "indicaciones_dueno": forms.Textarea(attrs={"rows": 3}),
        }


class VacunaForm(EstiloFormMixin, forms.ModelForm):
    class Meta:
        model = Vacuna
        fields = ["nombre", "lote", "fecha_proxima_aplicacion"]
        widgets = {
            # Esto hace que salga el calendario del navegador
            "fecha_proxima_aplicacion": forms.DateInput(attrs={"type": "date"}),
        }


class ArchivoAdjuntoForm(EstiloFormMixin, forms.ModelForm):
    class Meta:
        model = ArchivoAdjunto
        fields = ["archivo", "descripcion"]
        widgets = {
            "descripcion": forms.TextInput(
                attrs={"placeholder": "Descripción del archivo"}
            ),
        }


# --- 4. FORMSETS (La Fábrica) ---
# Aquí le decimos: "Usa estos formularios estilizados (form=...)"
VacunaFormSet = inlineformset_factory(
    HistoriaClinica,
    Vacuna,
    form=VacunaForm,  # <--- CLAVE: Usamos el form con estilo
    extra=1,
    can_delete=True,
)

ArchivoAdjuntoFormSet = inlineformset_factory(
    HistoriaClinica,
    ArchivoAdjunto,
    form=ArchivoAdjuntoForm,  # <--- CLAVE: Usamos el form con estilo
    extra=1,
    can_delete=True,
)
