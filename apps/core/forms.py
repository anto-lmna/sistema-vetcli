from django import forms
from django.utils import timezone
from apps.accounts.models import CustomUser, PerfilVeterinario


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


class CrearVeterinarioForm(forms.ModelForm):
    """Formulario para que el administrador cree un nuevo veterinario"""

    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        required=True,
        help_text="Nombre único para identificar al veterinario en el sistema.",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "ej: dr.lopez"}
        ),
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
        help_text="Debe tener al menos 8 caracteres.",
    )

    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
    )

    matricula = forms.CharField(
        label="Matrícula Profesional",
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "ej: MP-12345"}
        ),
    )

    especialidad = forms.CharField(
        label="Especialidad",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "ej: Medicina General"}
        ),
    )

    experiencia_anos = forms.IntegerField(
        label="Años de Experiencia",
        required=False,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "dni",
            "telefono",
            "direccion",
            "fecha_nacimiento",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Apellido"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}
            ),
            "dni": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "12345678"}
            ),
            "telefono": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+54 11 1234-5678"}
            ),
            "direccion": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Dirección completa"}
            ),
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo Electrónico",
            "dni": "DNI",
            "telefono": "Teléfono",
            "direccion": "Dirección",
            "fecha_nacimiento": "Fecha de Nacimiento",
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        if dni and CustomUser.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Este DNI ya está registrado.")
        return dni

    def clean_matricula(self):
        matricula = self.cleaned_data.get("matricula", "").strip().upper()
        if PerfilVeterinario.objects.filter(matricula__iexact=matricula).exists():
            raise forms.ValidationError("Esta matrícula ya está registrada.")
        return matricula

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        if password1 and len(password1) < 8:
            raise forms.ValidationError(
                "La contraseña debe tener al menos 8 caracteres."
            )
        return cleaned_data

    def save(self, commit=True, clinica=None):
        """
        Guarda el usuario veterinario y crea su perfil con matrícula
        """
        user = super().save(commit=False)
        user.rol = "veterinario"
        user.is_active = True
        user.set_password(self.cleaned_data["password1"])

        if clinica:
            user.clinica = clinica

        user._skip_perfil_creation = True

        if commit:
            user.save()

            PerfilVeterinario.objects.get_or_create(
                user=user,
                defaults={
                    "matricula": self.cleaned_data.get("matricula"),
                    "especialidad": self.cleaned_data.get("especialidad", ""),
                    "experiencia_anos": self.cleaned_data.get("experiencia_anos", 0),
                },
            )

        return user


class ClienteFiltroForm(forms.Form):
    """Formulario para filtrar clientes"""

    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Buscar por nombre, email o teléfono...",
            }
        ),
    )

    estado = forms.ChoiceField(
        required=False,
        choices=[
            ("", "Todos"),
            ("activo", "Activos"),
            ("inactivo", "Inactivos"),
            ("pendiente", "Pendientes de aprobación"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class VeterinarioFiltroForm(forms.Form):
    """Formulario para filtrar veterinarios"""

    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Buscar por nombre, email o matrícula...",
            }
        ),
    )

    estado = forms.ChoiceField(
        required=False,
        choices=[("", "Todos"), ("activo", "Activos"), ("inactivo", "Inactivos")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class PerfilVeterinarioForm(forms.ModelForm):
    class Meta:
        model = PerfilVeterinario
        fields = [
            "matricula",
            "especialidad",
            "telefono_profesional",
            "duracion_turno_default",
            "recibir_emails_reservas",
            "firma_digital",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
