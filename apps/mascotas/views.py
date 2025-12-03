from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    FormView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from apps.turnos.models import Turno, EstadoTurno
from .models import Mascota, Raza
from .forms import (
    MascotaClienteForm,
    MascotaAdminForm,
    InactivarMascotaForm,
    FiltroMascotasForm,
)


# ==================== MIXINS PERSONALIZADOS ====================


class ClienteRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea cliente"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.rol == "cliente"

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")


class AdminVeterinariaRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea administrador de veterinaria"""

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.rol == "admin_veterinaria"
        )

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")


class VeterinarioRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea veterinario"""

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.rol == "veterinario"
        )

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")


class MascotaOwnerMixin:
    """Mixin que verifica que el usuario sea dueño de la mascota"""

    def dispatch(self, request, *args, **kwargs):
        mascota = self.get_object()
        if request.user != mascota.dueno:
            messages.error(request, "No tienes permiso para editar esta mascota.")
            return redirect("mascotas:mis_mascotas")
        return super().dispatch(request, *args, **kwargs)


class MascotaClinicaMixin:
    """Mixin que verifica que la mascota pertenezca a la clínica del usuario"""

    def dispatch(self, request, *args, **kwargs):
        mascota = self.get_object()
        if mascota.dueno.clinica != request.user.clinica:
            messages.error(request, "Esta mascota no pertenece a tu clínica.")
            return redirect("mascotas:lista_mascotas_admin")
        return super().dispatch(request, *args, **kwargs)


class FiltroMascotasMixin:
    """Mixin para aplicar filtros comunes a listas de mascotas"""

    def get_queryset(self):
        queryset = super().get_queryset()

        # Crear formulario de filtros
        self.form_filtro = FiltroMascotasForm(self.request.GET)

        if self.form_filtro.is_valid():
            buscar = self.form_filtro.cleaned_data.get("buscar")
            especie = self.form_filtro.cleaned_data.get("especie")
            sexo = self.form_filtro.cleaned_data.get("sexo")
            estado = self.form_filtro.cleaned_data.get("estado")

            if buscar:
                # Para vistas de admin/veterinario, buscar también por dueño
                if hasattr(self, "buscar_por_dueno") and self.buscar_por_dueno:
                    queryset = queryset.filter(
                        Q(nombre__icontains=buscar)
                        | Q(dueno__first_name__icontains=buscar)
                        | Q(dueno__last_name__icontains=buscar)
                        | Q(dueno__email__icontains=buscar)
                    )
                else:
                    queryset = queryset.filter(nombre__icontains=buscar)

            if especie:
                queryset = queryset.filter(especie=especie)

            if sexo:
                queryset = queryset.filter(sexo=sexo)

            if estado == "activo":
                queryset = queryset.filter(activo=True)
            elif estado == "inactivo":
                queryset = queryset.filter(activo=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_filtro"] = self.form_filtro
        return context


# ==================== VISTAS PARA CLIENTES ====================


class MisMascotasListView(
    LoginRequiredMixin, ClienteRequiredMixin, FiltroMascotasMixin, ListView
):
    """Lista las mascotas del cliente autenticado"""

    model = Mascota
    template_name = "mascotas/mis_mascotas.html"
    context_object_name = "mascotas"
    buscar_por_dueno = False

    def get_queryset(self):
        queryset = (
            Mascota.objects.filter(dueno=self.request.user)
            .select_related("especie", "raza")
            .order_by("-activo", "nombre")
        )

        # Aplicar filtros del mixin padre
        self.form_filtro = FiltroMascotasForm(self.request.GET)
        if self.form_filtro.is_valid():
            buscar = self.form_filtro.cleaned_data.get("buscar")
            especie = self.form_filtro.cleaned_data.get("especie")
            sexo = self.form_filtro.cleaned_data.get("sexo")
            estado = self.form_filtro.cleaned_data.get("estado")

            if buscar:
                queryset = queryset.filter(nombre__icontains=buscar)
            if especie:
                queryset = queryset.filter(especie=especie)
            if sexo:
                queryset = queryset.filter(sexo=sexo)
            if estado == "activo":
                queryset = queryset.filter(activo=True)
            elif estado == "inactivo":
                queryset = queryset.filter(activo=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mascotas = self.get_queryset()
        context.update(
            {
                "total_mascotas": mascotas.count(),
                "activas": mascotas.filter(activo=True).count(),
                "inactivas": mascotas.filter(activo=False).count(),
            }
        )
        return context


class AgregarMascotaView(LoginRequiredMixin, ClienteRequiredMixin, CreateView):
    """Permite al cliente agregar una nueva mascota"""

    model = Mascota
    form_class = MascotaClienteForm
    template_name = "mascotas/agregar_mascota.html"
    success_url = reverse_lazy("mascotas:mis_mascotas")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'¡Mascota "{self.object.nombre}" agregada exitosamente!'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Agregar Nueva Mascota"
        return context


class EditarMascotaView(
    LoginRequiredMixin, ClienteRequiredMixin, MascotaOwnerMixin, UpdateView
):
    """Permite al cliente editar su mascota"""

    model = Mascota
    form_class = MascotaClienteForm
    template_name = "mascotas/editar_mascota.html"

    def get_success_url(self):
        return reverse_lazy("mascotas:detalle_mascota", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'Mascota "{self.object.nombre}" actualizada exitosamente.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f"Editar {self.object.nombre}"
        return context


class DetalleMascotaView(LoginRequiredMixin, DetailView):
    """Muestra los detalles de una mascota"""

    model = Mascota
    template_name = "mascotas/detalle_mascota.html"
    context_object_name = "mascota"

    def get_queryset(self):
        return Mascota.objects.select_related("especie", "raza", "dueno")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.rol == "veterinario":
            turno_activo = Turno.objects.filter(
                mascota=self.object,
                veterinario=self.request.user,
                estado__codigo=EstadoTurno.EN_CURSO,
            ).first()
            context["turno_activo"] = turno_activo

        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            mascota = self.get_object()
        except Mascota.DoesNotExist:
            return super().dispatch(request, *args, **kwargs)
        if request.user.rol == "cliente":
            if mascota.dueno != request.user:
                messages.error(request, "No tienes permiso para ver esta mascota.")
                return redirect("mascotas:mis_mascotas")
        elif request.user.rol not in ["admin_veterinaria", "veterinario"]:
            return HttpResponseForbidden("No tienes permiso para acceder.")

        return super().dispatch(request, *args, **kwargs)


# ==================== VISTAS PARA ADMIN ====================


class ListaMascotasAdminView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, FiltroMascotasMixin, ListView
):
    """Lista todas las mascotas de la clínica (solo admin)"""

    model = Mascota
    template_name = "mascotas/lista_mascotas_admin.html"
    context_object_name = "page_obj"
    paginate_by = 20
    buscar_por_dueno = True

    def get_queryset(self):
        queryset = (
            Mascota.objects.filter(dueno__clinica=self.request.user.clinica)
            .select_related("dueno")
            .order_by("-fecha_registro")
        )

        # Aplicar filtros del mixin padre
        self.form_filtro = FiltroMascotasForm(self.request.GET)
        if self.form_filtro.is_valid():
            buscar = self.form_filtro.cleaned_data.get("buscar")
            especie = self.form_filtro.cleaned_data.get("especie")
            sexo = self.form_filtro.cleaned_data.get("sexo")
            estado = self.form_filtro.cleaned_data.get("estado")

            if buscar:
                queryset = queryset.filter(
                    Q(nombre__icontains=buscar)
                    | Q(dueno__first_name__icontains=buscar)
                    | Q(dueno__last_name__icontains=buscar)
                    | Q(dueno__email__icontains=buscar)
                )
            if especie:
                queryset = queryset.filter(especie=especie)
            if sexo:
                queryset = queryset.filter(sexo=sexo)
            if estado == "activo":
                queryset = queryset.filter(activo=True)
            elif estado == "inactivo":
                queryset = queryset.filter(activo=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinica = self.request.user.clinica
        context.update(
            {
                "total_mascotas": self.get_queryset().count(),
                "activas": Mascota.objects.filter(
                    dueno__clinica=clinica, activo=True
                ).count(),
                "inactivas": Mascota.objects.filter(
                    dueno__clinica=clinica, activo=False
                ).count(),
            }
        )
        return context


class CrearMascotaAdminView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, CreateView
):
    """Permite al admin crear una mascota para un cliente"""

    model = Mascota
    form_class = MascotaAdminForm
    template_name = "mascotas/crear_mascota_admin.html"
    success_url = reverse_lazy("mascotas:lista_mascotas_admin")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Mascota "{self.object.nombre}" creada exitosamente para {self.object.dueno.get_full_name}.',
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Crear Nueva Mascota"
        return context


class EditarMascotaAdminView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, MascotaClinicaMixin, UpdateView
):
    """Permite al admin editar cualquier mascota"""

    model = Mascota
    form_class = MascotaAdminForm
    template_name = "mascotas/editar_mascota_admin.html"

    def get_success_url(self):
        return reverse_lazy("mascotas:detalle_mascota", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'Mascota "{self.object.nombre}" actualizada exitosamente.'
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f"Editar {self.object.nombre}"
        return context


class InactivarMascotaView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, MascotaClinicaMixin, FormView
):
    """Permite al admin inactivar una mascota"""

    form_class = InactivarMascotaForm
    template_name = "mascotas/inactivar_mascota.html"
    success_url = reverse_lazy("mascotas:lista_mascotas_admin")

    def get_object(self):
        """Obtener la mascota a inactivar"""
        if not hasattr(self, "_object"):
            self._object = get_object_or_404(Mascota, pk=self.kwargs["pk"])
        return self._object

    def form_valid(self, form):
        mascota = self.get_object()
        fecha_fallecimiento = form.cleaned_data.get("fecha_fallecimiento")
        mascota.inactivar(fecha_fallecimiento)

        mensaje = f'Mascota "{mascota.nombre}" inactivada exitosamente.'
        if fecha_fallecimiento:
            mensaje += (
                f' Fecha de fallecimiento: {fecha_fallecimiento.strftime("%d/%m/%Y")}'
            )

        messages.success(self.request, mensaje)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mascota"] = self.get_object()
        return context


class ActivarMascotaView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, MascotaClinicaMixin, View
):
    """Permite al admin reactivar una mascota"""

    def get_object(self):
        """Obtener la mascota a activar"""
        return get_object_or_404(Mascota, pk=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        """Mostrar confirmación"""
        mascota = self.get_object()
        return render(request, "mascotas/activar_mascota.html", {"mascota": mascota})

    def post(self, request, *args, **kwargs):
        """Activar la mascota"""
        mascota = self.get_object()
        mascota.activar()
        messages.success(
            request, f'Mascota "{mascota.nombre}" reactivada exitosamente.'
        )
        return redirect("mascotas:detalle_mascota", pk=mascota.pk)


# ==================== VISTAS PARA VETERINARIOS ====================


class ListaMascotasVeterinarioView(
    LoginRequiredMixin, VeterinarioRequiredMixin, FiltroMascotasMixin, ListView
):
    """Lista las mascotas de la clínica (para veterinarios)"""

    model = Mascota
    template_name = "mascotas/lista_mascotas_veterinario.html"
    context_object_name = "page_obj"
    paginate_by = 20
    buscar_por_dueno = True

    def get_queryset(self):
        queryset = (
            Mascota.objects.filter(dueno__clinica=self.request.user.clinica)
            .select_related("dueno")
            .order_by("-fecha_registro")
        )

        # Aplicar filtros del mixin padre
        self.form_filtro = FiltroMascotasForm(self.request.GET)
        if self.form_filtro.is_valid():
            buscar = self.form_filtro.cleaned_data.get("buscar")
            especie = self.form_filtro.cleaned_data.get("especie")
            sexo = self.form_filtro.cleaned_data.get("sexo")

            if buscar:
                queryset = queryset.filter(
                    Q(nombre__icontains=buscar)
                    | Q(dueno__first_name__icontains=buscar)
                    | Q(dueno__last_name__icontains=buscar)
                    | Q(dueno__email__icontains=buscar)
                )
            if especie:
                queryset = queryset.filter(especie=especie)
            if sexo:
                queryset = queryset.filter(sexo=sexo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mascotas"] = self.get_queryset().count()
        return context


# ==================== AJAX / API VIEWS ====================


class CargarRazasView(LoginRequiredMixin, View):
    """Devuelve las razas en formato JSON según la especie seleccionada"""

    def get(self, request, *args, **kwargs):
        especie_id = request.GET.get("especie_id")

        if especie_id:
            razas = (
                Raza.objects.filter(especie_id=especie_id, activo=True)
                .values("id", "nombre")
                .order_by("nombre")
            )
            return JsonResponse(list(razas), safe=False)

        return JsonResponse([], safe=False)
