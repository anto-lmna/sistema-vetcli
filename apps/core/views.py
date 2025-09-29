from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib import messages

from apps.clinicas.models import Clinica


class VeterinariaListView(ListView):
    """Vista principal - Lista todas las veterinarias disponibles"""

    model = Clinica
    template_name = "core/home.html"
    context_object_name = "veterinarias"

    def get_queryset(self):
        return Clinica.objects.filter(
            is_active=True, acepta_nuevos_clientes=True
        ).order_by("nombre")


def home_view(request):
    """Página de inicio - muestra lista de veterinarias"""
    veterinarias = Clinica.objects.filter(
        is_active=True, acepta_nuevos_clientes=True
    ).order_by("nombre")

    context = {"veterinarias": veterinarias, "total_veterinarias": veterinarias.count()}
    return render(request, "core/home.html", context)


@login_required
def dashboard_view(request):
    """Dashboard - redirige según el rol del usuario"""
    user = request.user

    if user.is_admin_veterinaria:
        return redirect("core:dashboard_admin")
    elif user.is_veterinario:
        return redirect("core:dashboard_veterinario")
    elif user.is_cliente:
        return redirect("core:dashboard_cliente")

    return render(request, "core/dashboard.html")


@login_required
def dashboard_admin_view(request):
    """Dashboard para administradores de veterinaria"""
    if not request.user.is_admin_veterinaria:
        messages.error(request, "No tienes permisos de administrador")
        return redirect("core:home")

    try:
        clinica = Clinica.objects.get(admin=request.user)
    except Clinica.DoesNotExist:
        messages.error(request, "No tienes una clínica asignada")
        return redirect("core:home")

    context = {
        "user": request.user,
        "clinica": clinica,
        "clientes_pendientes": clinica.clientes_pendientes(),
        "total_clientes_pendientes": clinica.total_clientes_pendientes(),
        "total_veterinarios": clinica.total_veterinarios,
    }

    return render(request, "core/dashboard_admin.html", context)


@login_required
def dashboard_veterinario_view(request):
    """Dashboard para veterinarios"""
    if not request.user.is_veterinario:
        messages.error(request, "No tienes permisos de veterinario")
        return redirect("core:home")

    if not hasattr(request.user, "perfilveterinario"):
        messages.error(request, "No tienes perfil de veterinario")
        return redirect("core:home")

    # La clínica está en user.clinica, no en perfilveterinario.clinica
    clinica = request.user.clinica

    context = {
        "user": request.user,
        "clinica": clinica,
        "perfil": request.user.perfilveterinario,
    }

    return render(request, "core/dashboard_veterinario.html", context)


@login_required
def dashboard_cliente_view(request):
    """Dashboard para clientes"""
    if not request.user.is_cliente:
        messages.error(request, "No tienes permisos de cliente")
        return redirect("core:home")

    if not hasattr(request.user, "perfilcliente"):
        messages.error(request, "No tienes perfil de cliente")
        return redirect("core:home")

    # La clínica está en user.clinica, no en perfilcliente.clinica
    clinica = request.user.clinica

    context = {
        "user": request.user,
        "clinica": clinica,
        "perfil": request.user.perfilcliente,
    }

    return render(request, "core/dashboard_cliente.html", context)
