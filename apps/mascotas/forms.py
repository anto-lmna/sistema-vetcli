from django import forms
from datetime import date

from .models import Mascota, Especie, Raza


class MascotaForm(forms.ModelForm):
    """Formulario base para crear/editar mascotas"""

    class Meta:
        model = Mascota
        fields = [
            "nombre",
            "especie",
            "raza",
            "sexo",
            "fecha_nacimiento",
            "color",
            "peso",
            "numero_chip",
            "foto",
            "esterilizado",
            "alergias",
            "condiciones_preexistentes",
            "observaciones",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Max, Luna, Rocky...",
                }
            ),
            "especie": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_especie",  # Para filtrar razas con JS
                }
            ),
            "raza": forms.Select(attrs={"class": "form-select", "id": "id_raza"}),
            "sexo": forms.Select(attrs={"class": "form-select"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "max": date.today().isoformat(),  # No puede ser fecha futura
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Negro, Blanco con manchas marrones...",
                }
            ),
            "peso": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Peso en kilogramos",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "numero_chip": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Número de microchip (opcional)",
                }
            ),
            "foto": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
            "esterilizado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "alergias": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Alergias a medicamentos, alimentos, etc. (opcional)",
                }
            ),
            "condiciones_preexistentes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Condiciones médicas crónicas o importantes (opcional)",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Cualquier información adicional relevante (opcional)",
                }
            ),
        }
        labels = {
            "nombre": "Nombre de la mascota",
            "especie": "Especie",
            "raza": "Raza",
            "sexo": "Sexo",
            "fecha_nacimiento": "Fecha de nacimiento (aproximada)",
            "color": "Color/Descripción física",
            "peso": "Peso (kg)",
            "numero_chip": "Número de microchip",
            "foto": "Foto de la mascota",
            "esterilizado": "¿Está esterilizado/castrado?",
            "alergias": "Alergias conocidas",
            "condiciones_preexistentes": "Condiciones médicas preexistentes",
            "observaciones": "Observaciones generales",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hacer campos opcionales más claros
        self.fields["fecha_nacimiento"].required = False
        self.fields["raza"].required = False
        self.fields["color"].required = False
        self.fields["peso"].required = False
        self.fields["numero_chip"].required = False
        self.fields["foto"].required = False

        # Si hay una especie seleccionada, filtrar las razas
        if "especie" in self.data:
            try:
                especie_id = int(self.data.get("especie"))
                self.fields["raza"].queryset = Raza.objects.filter(
                    especie_id=especie_id, activo=True
                ).order_by("nombre")
            except (ValueError, TypeError):
                self.fields["raza"].queryset = Raza.objects.none()
        elif self.instance.pk and self.instance.especie:
            self.fields["raza"].queryset = Raza.objects.filter(
                especie=self.instance.especie, activo=True
            ).order_by("nombre")
        else:
            self.fields["raza"].queryset = Raza.objects.none()

        # Filtrar solo especies activas
        self.fields["especie"].queryset = Especie.objects.filter(activo=True)

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and fecha > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha

    def clean_peso(self):
        peso = self.cleaned_data.get("peso")
        if peso and peso <= 0:
            raise forms.ValidationError("El peso debe ser mayor a 0.")
        if peso and peso > 500:
            raise forms.ValidationError("El peso parece incorrecto. Verifica el valor.")
        return peso

    def clean_numero_chip(self):
        numero_chip = self.cleaned_data.get("numero_chip")
        # Si está vacío, retornar None para evitar problemas con unique
        if not numero_chip or numero_chip.strip() == "":
            return None
        return numero_chip.strip()


class MascotaClienteForm(MascotaForm):
    """Formulario para que los clientes agreguen sus mascotas"""

    class Meta(MascotaForm.Meta):
        # Los clientes no pueden modificar el campo 'activo'
        # ni fecha_fallecimiento (solo el admin)
        fields = [
            "nombre",
            "especie",
            "raza",
            "sexo",
            "fecha_nacimiento",
            "color",
            "peso",
            "numero_chip",
            "foto",
            "esterilizado",
            "alergias",
            "observaciones",
        ]

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        mascota = super().save(commit=False)

        # Asignar automáticamente el dueño
        if self.usuario:
            mascota.dueno = self.usuario

        # Las mascotas creadas por clientes siempre están activas
        mascota.activo = True

        if commit:
            mascota.save()
        return mascota


class MascotaAdminForm(MascotaForm):
    """Formulario para que el admin gestione mascotas"""

    class Meta(MascotaForm.Meta):
        # El admin puede modificar TODO, incluyendo estado y fecha fallecimiento
        fields = MascotaForm.Meta.fields + ["activo", "fecha_fallecimiento", "dueno"]
        widgets = {
            **MascotaForm.Meta.widgets,
            "dueno": forms.Select(attrs={"class": "form-select"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "fecha_fallecimiento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "max": date.today().isoformat(),
                }
            ),
        }
        labels = {
            **MascotaForm.Meta.labels,
            "dueno": "Dueño",
            "activo": "Mascota activa",
            "fecha_fallecimiento": "Fecha de fallecimiento",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar solo clientes de la clínica del admin
        from apps.accounts.models import CustomUser

        self.fields["dueno"].queryset = CustomUser.objects.filter(
            rol="cliente", is_active=True
        ).select_related("clinica")

    def clean(self):
        cleaned_data = super().clean()
        activo = cleaned_data.get("activo")
        fecha_fallecimiento = cleaned_data.get("fecha_fallecimiento")

        # Si tiene fecha de fallecimiento, debe estar inactiva
        if fecha_fallecimiento and activo:
            raise forms.ValidationError("Una mascota fallecida no puede estar activa.")

        return cleaned_data


class InactivarMascotaForm(forms.Form):
    """Formulario simple para inactivar una mascota"""

    fecha_fallecimiento = forms.DateField(
        required=False,
        label="Fecha de fallecimiento (opcional)",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
                "max": date.today().isoformat(),
            }
        ),
        help_text="Dejar en blanco si solo se desea inactivar temporalmente",
    )
    motivo = forms.CharField(
        required=False,
        label="Motivo de inactivación",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Motivo por el cual se inactiva la mascota (opcional)",
            }
        ),
    )

    def clean_fecha_fallecimiento(self):
        fecha = self.cleaned_data.get("fecha_fallecimiento")
        if fecha and fecha > date.today():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return fecha


class FiltroMascotasForm(forms.Form):
    """Formulario para filtrar mascotas en listados"""

    buscar = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombre de mascota o dueño...",
            }
        ),
    )

    especie = forms.ModelChoiceField(
        queryset=Especie.objects.filter(activo=True),
        required=False,
        label="Especie",
        empty_label="Todas",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    sexo = forms.ChoiceField(
        choices=[("", "Todos")] + Mascota.SEXO_CHOICES,
        required=False,
        label="Sexo",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    estado = forms.ChoiceField(
        choices=[
            ("", "Todos"),
            ("activo", "Activos"),
            ("inactivo", "Inactivos"),
        ],
        required=False,
        label="Estado",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
