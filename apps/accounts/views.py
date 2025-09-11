from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from django.contrib.auth.views import LoginView
from django.views.generic import CreateView


from .forms import (
    CustomAuthenticationForm,
    ClientePreRegistroForm,
    AdminVeterinarioForm,
)


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        # Redirigir según el rol del usuario
        user = self.request.user
        if user.is_admin_veterinaria:
            return reverse_lazy("core:dashboard_admin")
        elif user.is_veterinario:
            return reverse_lazy("core:dashboard_veterinario")
        elif user.is_cliente:
            return reverse_lazy("core:dashboard_cliente")
        return reverse_lazy("core:dashboard")


class ClientePreRegistroView(CreateView):
    form_class = ClientePreRegistroForm
    template_name = "accounts/pre_registro_cliente.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Pre-registro exitoso. Si todo es correcto, tu cuenta será activada en las próximas horas",
        )
        return response


def registro_view(request):
    """Vista que muestra las opciones de registro"""
    return render(request, "accounts/registro_opciones.html")
