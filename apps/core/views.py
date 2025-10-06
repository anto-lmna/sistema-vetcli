from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib import messages

from apps.clinicas.models import Clinica
from apps.mascotas.models import Mascota
from apps.accounts.models import CustomUser


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

    messages.warning(request, "No tienes un rol asignado")
    return redirect("core:home")


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

    # Estadísticas de clientes
    clientes_pendientes = clinica.clientes_pendientes()
    total_clientes_pendientes = clinica.total_clientes_pendientes()

    # Estadísticas de veterinarios
    total_veterinarios = clinica.total_veterinarios

    # Estadísticas de clientes activos
    total_clientes = CustomUser.objects.filter(
        rol="cliente", clinica=clinica, is_active=True
    ).count()

    # Estadísticas de mascotas
    total_mascotas = Mascota.objects.filter(dueno__clinica=clinica).count()

    mascotas_activas = Mascota.objects.filter(
        dueno__clinica=clinica, activo=True
    ).count()

    mascotas_inactivas = Mascota.objects.filter(
        dueno__clinica=clinica, activo=False
    ).count()

    context = {
        "user": request.user,
        "clinica": clinica,
        "clientes_pendientes": clientes_pendientes[:10],  # Mostrar máximo 10
        "total_clientes_pendientes": total_clientes_pendientes,
        "total_veterinarios": total_veterinarios,
        "total_clientes": total_clientes,
        "total_mascotas": total_mascotas,
        "mascotas_activas": mascotas_activas,
        "mascotas_inactivas": mascotas_inactivas,
    }

    return render(request, "core/dashboard_admin.html", context)


@login_required
def dashboard_veterinario_view(request):
    """Dashboard para veterinarios"""
    if not request.user.is_veterinario:
        messages.error(request, "No tienes permisos de veterinario")
        return redirect("core:home")

    # Obtener clínica
    clinica = request.user.clinica

    if not clinica:
        messages.error(request, "No tienes una clínica asignada")
        return redirect("core:home")

    # Obtener perfil del veterinario (si existe)
    perfil = None
    if hasattr(request.user, "perfilveterinario"):
        perfil = request.user.perfilveterinario

    # Estadísticas
    total_mascotas = Mascota.objects.filter(dueno__clinica=clinica, activo=True).count()

    # Obtener las últimas 6 mascotas activas
    mascotas_recientes = (
        Mascota.objects.filter(dueno__clinica=clinica, activo=True)
        .select_related("especie", "raza", "dueno")
        .order_by("-fecha_registro")[:6]
    )

    context = {
        "user": request.user,
        "clinica": clinica,
        "perfil": perfil,
        "total_mascotas": total_mascotas,
        "mascotas_recientes": mascotas_recientes,
    }

    return render(request, "core/dashboard_veterinario.html", context)


@login_required
def dashboard_cliente_view(request):
    """Dashboard para clientes"""
    if not request.user.is_cliente:
        messages.error(request, "No tienes permisos de cliente")
        return redirect("core:home")

    # Obtener clínica
    clinica = request.user.clinica

    if not clinica:
        messages.error(request, "No tienes una clínica asignada")
        return redirect("core:home")

    # Obtener perfil del cliente (si existe)
    perfil = None
    if hasattr(request.user, "perfilcliente"):
        perfil = request.user.perfilcliente

    # Estadísticas del cliente
    total_mascotas = Mascota.objects.filter(dueno=request.user).count()

    # Obtener las últimas 3 mascotas para mostrar en el dashboard
    mascotas_recientes = (
        Mascota.objects.filter(dueno=request.user, activo=True)
        .select_related("especie", "raza")
        .order_by("-fecha_registro")[:3]
    )

    context = {
        "user": request.user,
        "clinica": clinica,
        "perfil": perfil,
        "total_mascotas": total_mascotas,
        "mascotas_recientes": mascotas_recientes,
    }

    return render(request, "core/dashboard_cliente.html", context)
