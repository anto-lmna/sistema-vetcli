from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, PerfilVeterinario, PerfilCliente


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
            "rol",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar el widget del rol
        self.fields["rol"].widget = forms.Select(choices=CustomUser.OPCIONES_ROL)

        # Personalizar labels y help texts
        self.fields["username"].label = "Nombre de usuario"
        self.fields["email"].label = "Correo electrónico"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["rol"].label = "Tipo de usuario"

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


class ClientePreRegistroForm(CustomUserCreationForm):
    """Formulario para pre-registro de clientes (queda pendiente de aprobación)"""

    contacto_emergencia = forms.CharField(
        max_length=100, required=False, label="Contacto de emergencia"
    )
    telefono_emergencia = forms.CharField(
        max_length=15, required=False, label="Teléfono de emergencia"
    )

    def __init__(self, *args, **kwargs):
        self.clinica = kwargs.pop("clinica", None)
        super().__init__(*args, **kwargs)
        # Solo permitir rol cliente
        self.fields["rol"].initial = "cliente"
        self.fields["rol"].widget = forms.HiddenInput()

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if self.clinica:
            # Verificar que no exista otro cliente con este email en la misma clínica
            # Cambiar para buscar en CustomUser.clinica en lugar de PerfilCliente.clinica
            existe = CustomUser.objects.filter(
                email=email, clinica=self.clinica, rol="cliente"
            ).exists()

            if existe:
                raise forms.ValidationError(
                    f"Ya existe un cliente con este email en {self.clinica.nombre}"
                )

        # Verificación general de email único
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = "cliente"
        user.is_active = False  # Inactivo hasta que admin apruebe
        user.pendiente_aprobacion = True
        user.clinica = self.clinica  # Asignar la clínica al usuario

        if commit:
            user.save()
            # El perfil se crea automáticamente por la señal, solo actualizamos
            user.perfilcliente.contacto_emergencia = self.cleaned_data.get(
                "contacto_emergencia", ""
            )
            user.perfilcliente.telefono_emergencia = self.cleaned_data.get(
                "telefono_emergencia", ""
            )
            user.perfilcliente.save()
        return user


class AdminVeterinarioForm(forms.ModelForm):
    """Formulario para que el admin cree veterinarios"""

    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirmar contraseña", widget=forms.PasswordInput
    )
    matricula = forms.CharField(max_length=20, required=True, label="Matrícula")
    especialidad = forms.CharField(max_length=100, required=False, label="Especialidad")
    experiencia_anos = forms.IntegerField(
        min_value=0, required=False, initial=0, label="Años de experiencia"
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "telefono", "dni")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def clean_matricula(self):
        matricula = self.cleaned_data.get("matricula")
        if PerfilVeterinario.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError("Ya existe un veterinario con esta matrícula.")
        return matricula

    def save(self, admin_user, clinica, commit=True):
        user = super().save(commit=False)
        user.rol = "veterinario"
        user.is_active = True
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # Crear perfil veterinario
            PerfilVeterinario.objects.create(
                user=user,
                matricula=self.cleaned_data.get("matricula"),
                especialidad=self.cleaned_data.get("especialidad", ""),
                experiencia_anos=self.cleaned_data.get("experiencia_anos", 0),
                clinica=clinica,
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
