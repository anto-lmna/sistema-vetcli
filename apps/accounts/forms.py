from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import CustomUser, PerfilVeterinario, PerfilCliente
from apps.clinicas.models import Clinica


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    telefono = forms.CharField(max_length=15, required=False, label="Teléfono")
    dni = forms.CharField(max_length=10, required=True, label="DNI")

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "telefono",
            "dni",
            "role",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar el widget del rol
        self.fields["role"].widget = forms.Select(choices=CustomUser.ROLE_CHOICES)

        # Personalizar labels y help texts
        self.fields["username"].label = "Nombre de usuario"
        self.fields["email"].label = "Correo electrónico"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["role"].label = "Tipo de usuario"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")
        return email

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        if CustomUser.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un usuario con este DNI.")
        return dni


class ClienteRegistroForm(CustomUserCreationForm):
    ocupacion = forms.CharField(max_length=100, required=False, label="Ocupación")
    contacto_emergencia = forms.CharField(
        max_length=100, required=False, label="Contacto de emergencia"
    )
    telefono_emergencia = forms.CharField(
        max_length=15, required=False, label="Teléfono de emergencia"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo permitir role cliente
        self.fields["role"].initial = "cliente"
        self.fields["role"].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "cliente"
        if commit:
            user.save()
            # Crear perfil cliente
            PerfilCliente.objects.create(
                user=user,
                ocupacion=self.cleaned_data.get("ocupacion", ""),
                contacto_emergencia=self.cleaned_data.get("contacto_emergencia", ""),
                telefono_emergencia=self.cleaned_data.get("telefono_emergencia", ""),
            )
        return user


class VeterinarioRegistroForm(CustomUserCreationForm):
    matricula = forms.CharField(max_length=20, required=True, label="Matrícula")
    especialidad = forms.CharField(max_length=100, required=False, label="Especialidad")
    experiencia_anos = forms.IntegerField(
        min_value=0, required=False, initial=0, label="Años de experiencia"
    )
    clinica = forms.ModelChoiceField(
        queryset=Clinica.objects.filter(is_active=True), required=False, label="Clínica"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo permitir role veterinario
        self.fields["role"].initial = "veterinario"
        self.fields["role"].widget = forms.HiddenInput()

    def clean_matricula(self):
        matricula = self.cleaned_data.get("matricula")
        if PerfilVeterinario.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError("Ya existe un veterinario con esta matrícula.")
        return matricula

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "veterinario"
        if commit:
            user.save()
            # Crear perfil veterinario
            PerfilVeterinario.objects.create(
                user=user,
                matricula=self.cleaned_data.get("matricula"),
                especialidad=self.cleaned_data.get("especialidad", ""),
                experiencia_anos=self.cleaned_data.get("experiencia_anos", 0),
                clinica=self.cleaned_data.get("clinica"),
            )
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o Email", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            # Permitir login con email o username
            if "@" in username:
                try:
                    user = CustomUser.objects.get(email=username)
                    username = user.username
                except CustomUser.DoesNotExist:
                    pass

            self.user_cache = authenticate(
                self.request, username=username, password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError("Usuario o contraseña incorrectos.")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
