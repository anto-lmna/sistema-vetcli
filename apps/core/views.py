from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import PerfilClienteForm
from apps.turnos.models import Turno
from apps.clinicas.models import Clinica
from apps.mascotas.models import Mascota
from apps.accounts.models import CustomUser


# ==================== MIXINS PERSONALIZADOS ====================


class AdminVeterinariaRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea administrador de veterinaria"""

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.is_admin_veterinaria
        )

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos de administrador")
        return redirect("core:home")


class VeterinarioRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea veterinario"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_veterinario

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos de veterinario")
        return redirect("core:home")


class ClienteRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea cliente"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_cliente

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos de cliente")
        return redirect("core:home")


# ==================== VISTAS PÚBLICAS ====================


class HomeView(ListView):
    """Página de inicio - muestra lista de veterinarias disponibles"""

    model = Clinica
    template_name = "core/home.html"
    context_object_name = "veterinarias"

    def get_queryset(self):
        return Clinica.objects.filter(
            is_active=True, acepta_nuevos_clientes=True
        ).order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_veterinarias"] = self.get_queryset().count()
        return context


# ==================== DASHBOARD PRINCIPAL ====================


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal - redirige según el rol del usuario"""

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.is_admin_veterinaria:
            return redirect("core:dashboard_admin")
        elif user.is_veterinario:
            return redirect("core:dashboard_veterinario")
        elif user.is_cliente:
            return redirect("core:dashboard_cliente")

        messages.warning(request, "No tienes un rol asignado")
        return redirect("core:home")


# ==================== DASHBOARD ADMINISTRADOR ====================


class DashboardAdminView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, TemplateView
):
    """Dashboard para administradores de veterinaria"""

    template_name = "core/dashboard_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            clinica = Clinica.objects.get(admin=user)
        except Clinica.DoesNotExist:
            messages.error(self.request, "No tienes una clínica asignada")
            return context

        # Estadísticas de clientes pendientes
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

        context.update(
            {
                "user": user,
                "clinica": clinica,
                "clientes_pendientes": clientes_pendientes[:10],  # Máximo 10
                "total_clientes_pendientes": total_clientes_pendientes,
                "total_veterinarios": total_veterinarios,
                "total_clientes": total_clientes,
                "total_mascotas": total_mascotas,
                "mascotas_activas": mascotas_activas,
                "mascotas_inactivas": mascotas_inactivas,
            }
        )

        return context


# ==================== DASHBOARD VETERINARIO ====================


class DashboardVeterinarioView(
    LoginRequiredMixin, VeterinarioRequiredMixin, TemplateView
):
    """Dashboard para veterinarios"""

    template_name = "core/dashboard_veterinario.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        clinica = user.clinica

        if not clinica:
            messages.error(self.request, "No tienes una clínica asignada")
            return context

        # Obtener perfil del veterinario (si existe)
        perfil = getattr(user, "perfilveterinario", None)

        # Estadísticas
        total_mascotas = Mascota.objects.filter(
            dueno__clinica=clinica, activo=True
        ).count()

        # Últimas 6 mascotas activas
        mascotas_recientes = (
            Mascota.objects.filter(dueno__clinica=clinica, activo=True)
            .select_related("especie", "raza", "dueno")
            .order_by("-fecha_registro")[:6]
        )

        # Turnos de hoy
        hoy = timezone.localdate()
        turnos_hoy = Turno.objects.filter(
            veterinario=user, reservado=True, cliente__isnull=False, fecha=hoy
        ).count()

        context.update(
            {
                "user": user,
                "clinica": clinica,
                "perfil": perfil,
                "total_mascotas": total_mascotas,
                "mascotas_recientes": mascotas_recientes,
                "turnos_hoy": turnos_hoy,
            }
        )

        return context


# ==================== DASHBOARD CLIENTE ====================


class DashboardClienteView(LoginRequiredMixin, ClienteRequiredMixin, TemplateView):
    """Dashboard para clientes"""

    template_name = "core/dashboard_cliente.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        clinica = user.clinica

        if not clinica:
            messages.error(self.request, "No tienes una clínica asignada")
            return context

        # Obtener perfil del cliente (si existe)
        perfil = getattr(user, "perfilcliente", None)

        # Estadísticas del cliente
        total_mascotas = Mascota.objects.filter(dueno=user).count()
        hoy = timezone.now().date()

        # Turnos pendientes (por venir)
        turnos_pendientes = Turno.objects.filter(
            cliente=user,
            fecha__gte=hoy,
            estado__codigo__in=["pendiente", "confirmado"],
        ).count()

        # Últimas 3 mascotas
        mascotas_recientes = (
            Mascota.objects.filter(dueno=user, activo=True)
            .select_related("especie", "raza")
            .order_by("-fecha_registro")[:3]
        )

        context.update(
            {
                "user": user,
                "clinica": clinica,
                "perfil": perfil,
                "total_mascotas": total_mascotas,
                "mascotas_recientes": mascotas_recientes,
                "turnos_pendientes": turnos_pendientes,
            }
        )

        return context


# ==================== PERFIL CLIENTE ====================


class PerfilClienteView(LoginRequiredMixin, ClienteRequiredMixin, TemplateView):
    """Vista de perfil del cliente (solo lectura)"""

    template_name = "core/perfil_cliente.html"

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


class PerfilClienteUpdateView(LoginRequiredMixin, ClienteRequiredMixin, UpdateView):
    """Vista para editar perfil del cliente"""

    model = CustomUser
    form_class = PerfilClienteForm
    template_name = "core/perfil_cliente_editar.html"
    success_url = reverse_lazy("core:perfil_cliente")

    def get_object(self):
        """El objeto a editar siempre es el usuario actual"""
        return self.request.user

    def form_valid(self, form):
        """Preservar fecha de nacimiento si no se modificó"""
        if not form.cleaned_data.get("fecha_nacimiento"):
            form.instance.fecha_nacimiento = self.request.user.fecha_nacimiento

        messages.success(self.request, "Tu perfil se actualizó correctamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al actualizar tu perfil.")
        return super().form_invalid(form)


# ==================== GESTIÓN DE CLIENTES PENDIENTES ====================


class AprobarClienteView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, TemplateView
):
    """Aprobar un cliente pendiente"""

    def post(self, request, cliente_id):
        try:
            clinica = Clinica.objects.get(admin=request.user)
            cliente = CustomUser.objects.get(
                id=cliente_id, rol="cliente", clinica=clinica, pendiente_aprobacion=True
            )

            # Aprobar el cliente
            cliente.pendiente_aprobacion = False
            cliente.fecha_aprobacion = timezone.now()
            cliente.aprobado_por = request.user
            cliente.is_active = True
            cliente.save()

            messages.success(
                request, f"✅ Cliente {cliente.get_full_name()} aprobado exitosamente"
            )

        except Clinica.DoesNotExist:
            messages.error(request, "No tienes una clínica asignada")
        except CustomUser.DoesNotExist:
            messages.error(request, "Cliente no encontrado o ya fue procesado")

        return redirect("core:dashboard_admin")


class RechazarClienteView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, TemplateView
):
    """Rechazar y eliminar un cliente pendiente"""

    def post(self, request, cliente_id):
        try:
            clinica = Clinica.objects.get(admin=request.user)
            cliente = CustomUser.objects.get(
                id=cliente_id, rol="cliente", clinica=clinica, pendiente_aprobacion=True
            )

            # Guardar nombre antes de eliminar
            nombre_cliente = cliente.get_full_name()

            # Eliminar el cliente
            cliente.delete()

            messages.warning(
                request, f"Solicitud de {nombre_cliente} rechazada y eliminada"
            )

        except Clinica.DoesNotExist:
            messages.error(request, "No tienes una clínica asignada")
        except CustomUser.DoesNotExist:
            messages.error(request, "Cliente no encontrado o ya fue procesado")

        return redirect("core:dashboard_admin")
