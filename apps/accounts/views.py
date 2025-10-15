from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage # <-- agrego paginacion

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
    """Vista que muestra las opciones de registro con paginación de clínicas"""
    todas_las_clinicas = Clinica.objects.filter(
        is_active=True, acepta_nuevos_clientes=True
    ).order_by('nombre')
    
    paginator = Paginator(todas_las_clinicas, 2)
    page_number = request.GET.get('page')
    
    try:
        clinicas_disponibles_paginadas = paginator.get_page(page_number)
    except EmptyPage:
        # En caso de página vacía (ej: URL manipulada), ir a la última página
        clinicas_disponibles_paginadas = paginator.get_page(paginator.num_pages)
        
    # --- LÓGICA DE PAGINACIÓN TRUNCADA (2 páginas alrededor) ---
    rango_a_mostrar = 2
    current_page = clinicas_disponibles_paginadas.number
    total_pages = paginator.num_pages
    
    start_index = max(1, current_page - rango_a_mostrar)
    end_index = min(total_pages, current_page + rango_a_mostrar) + 1
    
    # Asegurar que el rango sea de 5 números si es posible (cerca de los bordes)
    if end_index - start_index < (2 * rango_a_mostrar + 1):
        if current_page <= rango_a_mostrar:
            end_index = min(total_pages + 1, (2 * rango_a_mostrar) + 2)
        elif current_page >= total_pages - rango_a_mostrar:
            start_index = max(1, total_pages - (2 * rango_a_mostrar))

    page_range_custom = range(start_index, end_index)

    context = {
        "clinicas_disponibles": clinicas_disponibles_paginadas,
        "total_clinicas": paginator.count,
        "page_range_custom": page_range_custom, 
        "show_ellipsis_start": start_index > 1, 
        "show_ellipsis_end": end_index <= total_pages, 
    }

    return render(request, "accounts/registro_opciones.html", context)


def logout_view(request):
    """Vista personalizada de logout que acepta GET"""
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente")
    return redirect("core:home")
