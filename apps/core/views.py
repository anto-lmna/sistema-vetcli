from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import (
    PerfilClienteForm,
    CrearVeterinarioForm,
    VeterinarioFiltroForm,
    ClienteFiltroForm,
)
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
        hoy = timezone.localdate()  # Mejor que timezone.now().date()

        # ---------------------------------------------------------
        # 1. DATOS DE TURNOS (QUERYSETS)
        # ---------------------------------------------------------
        # Esta es la LISTA completa para la tabla de "Agenda Hoy"
        turnos_hoy_qs = (
            Turno.objects.filter(veterinario=user, fecha=hoy, reservado=True)
            .select_related("mascota", "estado", "cliente")
            .order_by("hora_inicio")
        )

        # ---------------------------------------------------------
        # 2. MÉTRICAS (CONTADORES)
        # ---------------------------------------------------------
        # Total citas hoy
        count_turnos_hoy = turnos_hoy_qs.count()

        # Completados hoy (Éxito)
        count_completados = turnos_hoy_qs.filter(estado__codigo="completado").count()

        # Pendientes hoy (Sala de Espera: Confirmados + En Curso)
        # ESTO ES LO QUE PREGUNTABAS DE LA LISTA DE ESPERA
        count_pendientes = turnos_hoy_qs.filter(
            estado__codigo__in=["confirmado", "en_curso"]
        ).count()

        # ---------------------------------------------------------
        # 3. MASCOTAS RECIENTES (LOGICA MIXTA)
        # ---------------------------------------------------------
        # Preferimos mostrar mascotas que el vet atendió recientemente (completados)
        ultimos_turnos = (
            Turno.objects.filter(veterinario=user, estado__codigo="completado")
            .select_related("mascota__dueno")
            .order_by("-fecha", "-hora_inicio")[:5]
        )

        mascotas_vistas_recientemente = [t.mascota for t in ultimos_turnos]

        # Si no ha atendido a nadie, mostramos las últimas registradas en la clínica como fallback
        if not mascotas_vistas_recientemente:
            mascotas_vistas_recientemente = Mascota.objects.filter(
                dueno__clinica=clinica, activo=True
            ).order_by("-fecha_registro")[:5]

        # ---------------------------------------------------------
        # 4. ARMADO DEL CONTEXTO
        # ---------------------------------------------------------
        context.update(
            {
                "user": user,
                "clinica": clinica,
                "perfil": getattr(user, "perfilveterinario", None),
                # Listas
                "turnos_hoy": turnos_hoy_qs,  # Para la TABLA (QuerySet)
                "mascotas_recientes": mascotas_vistas_recientemente,  # Para el sidebar
                # Contadores (Números)
                "turnos_hoy_count": count_turnos_hoy,  # Para la Card Info
                "turnos_completados_hoy": count_completados,  # Para la Card Success
                "turnos_pendientes_hoy": count_pendientes,  # Para la Card Warning (Sala de Espera)
                "total_mascotas": Mascota.objects.filter(
                    dueno__clinica=clinica, activo=True
                ).count(),
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


# ==================== CREAR VETERINARIO ====================


class VeterinarioCreateView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, CreateView
):
    """Vista para crear veterinarios desde el dashboard del administrador"""

    model = CustomUser
    form_class = CrearVeterinarioForm
    template_name = "core/veterinario_crear.html"
    success_url = reverse_lazy("core:dashboard_admin")

    def form_valid(self, form):
        clinica = self.request.user.clinica
        form.save(clinica=clinica)
        messages.success(self.request, "✅ Veterinario creado exitosamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "❌ Ocurrió un error al crear el veterinario.")
        return super().form_invalid(form)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para verificar que el usuario sea administrador de veterinaria"""

    def test_func(self):
        return self.request.user.is_admin_veterinaria


# ==================== LISTAR CLIENTES Y VETERINARIOS ====================


class ListaClientesView(AdminRequiredMixin, ListView):
    """Vista para listar clientes (solo para admin)"""

    model = CustomUser
    template_name = "core/lista_clientes.html"
    context_object_name = "clientes"
    paginate_by = 15

    def get_queryset(self):
        queryset = (
            CustomUser.objects.filter(rol="cliente", clinica=self.request.user.clinica)
            .select_related("clinica")
            .order_by("-date_joined")
        )

        # Aplicar filtros del formulario
        buscar = self.request.GET.get("buscar", "")
        estado = self.request.GET.get("estado", "")

        if buscar:
            queryset = queryset.filter(
                Q(first_name__icontains=buscar)
                | Q(last_name__icontains=buscar)
                | Q(email__icontains=buscar)
                | Q(telefono__icontains=buscar)
            )

        if estado == "activo":
            queryset = queryset.filter(is_active=True, aprobado_por=True)
        elif estado == "inactivo":
            queryset = queryset.filter(is_active=False)
        elif estado == "pendiente":
            queryset = queryset.filter(aprobado_por=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar formulario de filtro
        context["form_filtro"] = ClienteFiltroForm(self.request.GET or None)

        # Estadísticas
        all_clientes = CustomUser.objects.filter(
            rol="cliente", clinica=self.request.user.clinica
        )
        context["total_clientes"] = all_clientes.count()
        context["activos"] = all_clientes.filter(
            is_active=True, aprobado_por=True
        ).count()
        context["inactivos"] = all_clientes.filter(is_active=False).count()
        context["pendientes"] = all_clientes.filter(aprobado_por=False).count()

        return context


class ListaVeterinariosView(AdminRequiredMixin, ListView):
    """Vista para listar veterinarios (solo para admin)"""

    model = CustomUser
    template_name = "core/lista_veterinarios.html"
    context_object_name = "veterinarios"
    paginate_by = 15

    def get_queryset(self):
        # Filtrar solo veterinarios de la clínica del admin
        queryset = (
            CustomUser.objects.filter(
                rol="veterinario", clinica=self.request.user.clinica
            )
            .select_related("clinica")
            .order_by("last_name", "first_name")
        )

        # Aplicar filtros del formulario
        buscar = self.request.GET.get("buscar", "")
        estado = self.request.GET.get("estado", "")

        if buscar:
            queryset = queryset.filter(
                Q(first_name__icontains=buscar)
                | Q(last_name__icontains=buscar)
                | Q(email__icontains=buscar)
            )

        if estado == "activo":
            queryset = queryset.filter(is_active=True)
        elif estado == "inactivo":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar formulario de filtro
        context["form_filtro"] = VeterinarioFiltroForm(self.request.GET or None)

        # Estadísticas
        all_veterinarios = CustomUser.objects.filter(
            rol="veterinario", clinica=self.request.user.clinica
        )
        context["total_veterinarios"] = all_veterinarios.count()
        context["activos"] = all_veterinarios.filter(is_active=True).count()
        context["inactivos"] = all_veterinarios.filter(is_active=False).count()

        return context
