from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

from .models import CustomUser
from .forms import ClienteFiltroForm, VeterinarioFiltroForm


from .forms import (
    CustomAuthenticationForm,
    ClientePreRegistroForm,
)
from apps.clinicas.models import Clinica


class CustomLoginView(LoginView):
    """Vista de login con redirección según rol"""

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
    """Vista de pre-registro de clientes con clínica opcional"""

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


class RegistroOpcionesView(ListView):
    """Vista que muestra opciones de registro con clínicas paginadas"""

    model = Clinica
    template_name = "accounts/registro_opciones.html"
    context_object_name = "clinicas_disponibles"
    paginate_by = 2

    def get_queryset(self):
        """Filtrar solo clínicas activas que aceptan nuevos clientes"""
        return Clinica.objects.filter(
            is_active=True, acepta_nuevos_clientes=True
        ).order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total de clínicas
        context["total_clinicas"] = self.get_queryset().count()

        # Obtener el objeto paginator y page_obj del contexto
        page_obj = context.get("page_obj")
        paginator = context.get("paginator")

        if page_obj and paginator:
            # Lógica de paginación truncada (2 páginas alrededor)
            rango_a_mostrar = 2
            current_page = page_obj.number
            total_pages = paginator.num_pages

            start_index = max(1, current_page - rango_a_mostrar)
            end_index = min(total_pages, current_page + rango_a_mostrar) + 1

            # Asegurar que el rango sea de 5 números si es posible (cerca de los bordes)
            if end_index - start_index < (2 * rango_a_mostrar + 1):
                if current_page <= rango_a_mostrar:
                    end_index = min(total_pages + 1, (2 * rango_a_mostrar) + 2)
                elif current_page >= total_pages - rango_a_mostrar:
                    start_index = max(1, total_pages - (2 * rango_a_mostrar))

            context["page_range_custom"] = range(start_index, end_index)
            context["show_ellipsis_start"] = start_index > 1
            context["show_ellipsis_end"] = end_index <= total_pages

        return context


class CustomLogoutView(View):
    """Vista personalizada de logout que acepta GET"""

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Has cerrado sesión exitosamente")
        return redirect("core:home")

    def post(self, request, *args, **kwargs):
        """También soporta POST para mayor seguridad"""
        return self.get(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin para verificar que el usuario sea administrador de veterinaria"""

    def test_func(self):
        return self.request.user.is_admin_veterinaria


class ListaClientesView(AdminRequiredMixin, ListView):
    """Vista para listar clientes (solo para admin)"""

    model = CustomUser
    template_name = "accounts/lista_clientes.html"
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
    template_name = "accounts/lista_veterinarios.html"
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
                | Q(matricula__icontains=buscar)
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
