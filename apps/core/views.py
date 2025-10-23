from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import PerfilClienteForm
from apps.turnos.models import Turno
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

    hoy = timezone.localdate()
    turnos_hoy = Turno.objects.filter(
        veterinario=request.user, reservado=True, cliente__isnull=False, fecha=hoy
    ).count()

    context = {
        "user": request.user,
        "clinica": clinica,
        "perfil": perfil,
        "total_mascotas": total_mascotas,
        "mascotas_recientes": mascotas_recientes,
        "turnos_hoy": turnos_hoy,
    }

    return render(request, "core/dashboard_veterinario.html", context)


# Cliente
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
    hoy = timezone.now().date()

    # Contar turnos pendientes (por venir)
    turnos_pendientes = Turno.objects.filter(
        cliente=request.user,
        fecha__gte=hoy,
        estado__codigo__in=["pendiente", "confirmado"],
    ).count()

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
        "turnos_pendientes": turnos_pendientes,
    }

    return render(request, "core/dashboard_cliente.html", context)


class PerfilClienteView(LoginRequiredMixin, TemplateView):
    template_name = "core/perfil_cliente.html"

    def dispatch(self, request, *args, **kwargs):
        # Verifica permisos de cliente antes de continuar
        if not request.user.is_cliente:
            messages.error(request, "No tienes permisos de cliente.")
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        perfil = getattr(user, "perfilcliente", None)
        clinica = user.clinica
        mascotas = Mascota.objects.filter(dueno=user).order_by("-fecha_registro")

        context.update(
            {
                "user": user,
                "perfil": perfil,
                "clinica": clinica,
                "mascotas": mascotas,
            }
        )
        return context


class PerfilClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = PerfilClienteForm
    template_name = "core/perfil_cliente_editar.html"
    success_url = reverse_lazy("core:perfil_cliente")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        if not form.cleaned_data.get("fecha_nacimiento"):
            form.instance.fecha_nacimiento = self.request.user.fecha_nacimiento
        messages.success(self.request, "Tu perfil se actualizó correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al actualizar tu perfil.")
        return super().form_invalid(form)
