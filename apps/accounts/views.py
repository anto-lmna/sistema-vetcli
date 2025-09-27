from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, render, get_object_or_404

from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView

from .forms import (
    CustomAuthenticationForm,
    ClientePreRegistroForm,
)
from apps.clinicas.models import Clinica


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "accounts/login.html"

    def get_success_url(self):
        user = self.request.user

        # Redirigir según el rol del usuario
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
    success_url = reverse_lazy("accounts:registro_exitoso")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinica_slug = self.kwargs.get("clinica_slug")
        if clinica_slug:
            context["clinica"] = get_object_or_404(
                Clinica,
                slug=clinica_slug,
                is_active=True,
                acepta_nuevos_clientes=True,
            )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        clinica_slug = self.kwargs.get("clinica_slug")
        if clinica_slug:
            clinica = get_object_or_404(
                Clinica,
                slug=clinica_slug,
                is_active=True,
                acepta_nuevos_clientes=True,
            )
            kwargs["clinica"] = clinica
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        if hasattr(form, "clinica") and form.clinica:
            messages.success(
                self.request,
                f"¡Pre-registro exitoso en {form.clinica.nombre}! "
                "Te contactaremos pronto para activar tu cuenta.",
            )
        else:
            messages.success(
                self.request,
                "Pre-registro exitoso. Tu cuenta será activada en las próximas horas",
            )
        return response


class RegistroExitosoView(TemplateView):
    """Vista para mostrar confirmación de registro exitoso"""

    template_name = "accounts/registro_exitoso.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar lista de clínicas disponibles
        context["clinicas_disponibles"] = Clinica.objects.filter(
            is_active=True, acepta_nuevos_clientes=True
        ).count()
        return context


def registro_view(request):
    """Vista que muestra las opciones de registro"""
    # Mostrar clínicas disponibles para pre-registro
    clinicas_disponibles = Clinica.objects.filter(
        is_active=True, acepta_nuevos_clientes=True
    )

    context = {
        "clinicas_disponibles": clinicas_disponibles,
        "total_clinicas": clinicas_disponibles.count(),
    }

    return render(request, "accounts/registro_opciones.html", context)


def logout_view(request):
    """Vista personalizada de logout que acepta GET"""
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente")
    return redirect("core:home")
