from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db import transaction
from datetime import datetime
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from apps.accounts.models import CustomUser
from apps.mascotas.models import Mascota
from .forms import TurnoCrearAdminForm
from .models import Turno, DisponibilidadVeterinario, EstadoTurno


# ==================== MIXINS PERSONALIZADOS ====================


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


class AdminVeterinariaRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea admin de veterinaria"""

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.rol == "admin_veterinaria"
        )

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")


class ClienteRequiredMixin(UserPassesTestMixin):
    """Mixin que verifica que el usuario sea cliente"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.rol == "cliente"

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")


class VetOrAdminMixin(UserPassesTestMixin):
    """Mixin que permite acceso a veterinarios y admins"""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.rol in [
            "veterinario",
            "admin_veterinaria",
        ]

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para acceder a esta página.")
        return redirect("core:dashboard")


# ==================== VETERINARIO - DISPONIBILIDAD ====================


class DisponibilidadListView(LoginRequiredMixin, VetOrAdminMixin, ListView):
    """Lista de disponibilidades del veterinario"""

    model = DisponibilidadVeterinario
    template_name = "turnos/disponibilidad_list.html"
    context_object_name = "disponibilidades"

    def get_queryset(self):
        if hasattr(self, "_queryset_cache"):
            return self._queryset_cache

        qs = DisponibilidadVeterinario.objects.filter(
            veterinario=self.request.user
        ).order_by("-fecha_inicio")

        # Filtro por estado (futuras/pasadas)
        filtro = self.request.GET.get("filtro", "futuras")
        hoy = timezone.now().date()

        if filtro == "pasadas":
            qs = qs.filter(fecha_fin__lt=hoy)
        else:
            qs = qs.filter(fecha_fin__gte=hoy)

        # Filtro por fecha específica
        fecha_busqueda = self.request.GET.get("buscar_fecha")
        if fecha_busqueda:
            qs = qs.filter(
                fecha_inicio__lte=fecha_busqueda, fecha_fin__gte=fecha_busqueda
            )

        self._queryset_cache = qs
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.now().date()
        context["filtro_actual"] = self.request.GET.get("filtro", "futuras")
        return context


class DisponibilidadCreateView(
    LoginRequiredMixin, VeterinarioRequiredMixin, CreateView
):
    """Crear nueva disponibilidad y generar turnos"""

    model = DisponibilidadVeterinario
    fields = ["fecha_inicio", "fecha_fin", "hora_inicio", "hora_fin", "duracion_turno"]
    template_name = "turnos/disponibilidad_form.html"
    success_url = reverse_lazy("turnos:disponibilidades")

    def form_valid(self, form):
        user = self.request.user
        clinica = user.clinica

        inicio = form.cleaned_data["hora_inicio"]
        fin = form.cleaned_data["hora_fin"]

        # Validar horario dentro del horario de la clínica
        if inicio < clinica.hora_apertura or fin > clinica.hora_cierre:
            messages.error(
                self.request,
                f"El horario está fuera del horario de atención de la clínica "
                f"({clinica.hora_apertura.strftime('%H:%M')} - {clinica.hora_cierre.strftime('%H:%M')}).",
            )
            return self.form_invalid(form)

        # Validar fechas
        fecha_inicio = form.cleaned_data["fecha_inicio"]
        fecha_fin = form.cleaned_data["fecha_fin"]

        if fecha_fin < fecha_inicio:
            messages.error(
                self.request,
                "La fecha de fin no puede ser anterior a la fecha de inicio.",
            )
            return self.form_invalid(form)

        # Asignar veterinario y clínica
        form.instance.veterinario = user
        form.instance.clinica = clinica
        response = super().form_valid(form)

        # Generar turnos automáticamente
        form.instance.generar_turnos_rango()

        messages.success(
            self.request, "Disponibilidad creada y turnos generados correctamente."
        )
        return response


class DisponibilidadDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar disponibilidad (y sus turnos no reservados)"""

    model = DisponibilidadVeterinario
    template_name = "turnos/disponibilidad_confirm_delete.html"
    success_url = reverse_lazy("turnos:disponibilidades")

    def test_func(self):
        disp = self.get_object()
        return self.request.user == disp.veterinario

    def delete(self, request, *args, **kwargs):
        disp = self.get_object()

        # Validar fechas válidas
        if not disp.fecha_inicio or not disp.fecha_fin:
            messages.error(request, "La disponibilidad no tiene fechas válidas.")
            return redirect("turnos:disponibilidades")

        # Contar turnos reservados dentro del rango
        turnos_reservados = Turno.objects.filter(
            veterinario=disp.veterinario,
            clinica=disp.clinica,
            fecha__range=(disp.fecha_inicio, disp.fecha_fin),
            hora_inicio__gte=disp.hora_inicio,
            hora_inicio__lt=disp.hora_fin,
            reservado=True,
        ).count()

        if turnos_reservados > 0:
            messages.error(
                request,
                f"No se puede eliminar. Hay {turnos_reservados} turno(s) ya reservado(s) en este rango.",
            )
            return redirect("turnos:disponibilidades")

        # Eliminar los turnos disponibles (no reservados)
        turnos_eliminados = Turno.objects.filter(
            veterinario=disp.veterinario,
            clinica=disp.clinica,
            fecha__range=(disp.fecha_inicio, disp.fecha_fin),
            hora_inicio__gte=disp.hora_inicio,
            hora_inicio__lt=disp.hora_fin,
            reservado=False,
        ).delete()[0]

        messages.success(
            request,
            f"Disponibilidad eliminada. {turnos_eliminados} turno(s) disponible(s) eliminado(s).",
        )

        return super().delete(request, *args, **kwargs)


# ==================== VETERINARIO - AGENDA ====================


class AgendaVeterinarioView(LoginRequiredMixin, VeterinarioRequiredMixin, ListView):
    """Agenda del veterinario con sus turnos reservados"""

    model = Turno
    template_name = "turnos/agenda_veterinario.html"
    context_object_name = "turnos"

    def get_queryset(self):
        return (
            Turno.objects.filter(
                veterinario=self.request.user,
                reservado=True,
                cliente__isnull=False,
                fecha__gte=timezone.now().date(),
            )
            .select_related("estado", "cliente", "mascota")
            .order_by("fecha", "hora_inicio")
            .exclude(estado__codigo__in=["completado", "cancelado", "no_asistio"])
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas de turnos de hoy
        turnos_hoy = self.get_queryset().filter(fecha=timezone.now().date())
        context["turnos_hoy"] = turnos_hoy
        context["total_turnos_hoy"] = turnos_hoy.count()

        return context


class TurnoDetalleVeterinarioView(LoginRequiredMixin, DetailView):
    """Ver detalle de un turno (veterinario)"""

    model = Turno
    template_name = "turnos/turno_detalle_veterinario.html"
    context_object_name = "turno"

    def test_func(self):
        turno = self.get_object()
        return self.request.user == turno.veterinario


# ==================== VETERINARIO - ACCIONES DE TURNO ====================


class BaseTurnoAccionView(LoginRequiredMixin, VeterinarioRequiredMixin, View):
    """Clase base para acciones de turnos del veterinario"""

    def get_turno(self, pk):
        """Obtiene el turno y verifica que sea del veterinario"""
        return get_object_or_404(Turno, pk=pk, veterinario=self.request.user)


# class TurnoIniciarAtencionView(BaseTurnoAccionView):
#     """Marcar turno como 'En curso'"""

#     def post(self, request, pk):
#         turno = self.get_turno(pk)

#         if not turno.reservado:
#             messages.error(request, "No se puede iniciar un turno no reservado.")
#             return redirect("turnos:agenda_vet")

#         if turno.estado.codigo != EstadoTurno.CONFIRMADO:
#             messages.warning(
#                 request, f"El turno ya está en estado {turno.estado.nombre}."
#             )
#             return redirect("turnos:agenda_vet")

#         estado_en_curso = EstadoTurno.objects.get(codigo=EstadoTurno.EN_CURSO)
#         turno.estado = estado_en_curso
#         turno.save()

#         messages.info(request, f"Atención de {turno.mascota.nombre} iniciada.")
#         return redirect("turnos:turno_detalle_vet", pk=pk)


class TurnoIniciarAtencionView(BaseTurnoAccionView):
    """Marcar turno como 'En curso' y redirigir a Historia Clínica"""

    def post(self, request, pk):
        turno = self.get_turno(pk)

        if not turno.reservado:
            messages.error(request, "No se puede iniciar un turno no reservado.")
            return redirect("turnos:agenda_vet")

        if turno.estado.codigo == EstadoTurno.CONFIRMADO:
            estado_en_curso = EstadoTurno.objects.get(codigo=EstadoTurno.EN_CURSO)
            turno.estado = estado_en_curso
            turno.save()

        url_historia = reverse(
            "historias:crear_historia", kwargs={"mascota_id": turno.mascota.id}
        )

        return redirect(f"{url_historia}?turno_id={turno.pk}")


class TurnoCompletarView(BaseTurnoAccionView):
    """Marcar turno como completado"""

    def post(self, request, pk):
        turno = self.get_turno(pk)

        if not turno.reservado:
            messages.error(request, "No se puede completar un turno no reservado.")
            return redirect("turnos:agenda_vet")

        estado_completado = EstadoTurno.objects.get(codigo=EstadoTurno.COMPLETADO)
        turno.estado = estado_completado
        turno.save()

        messages.success(
            request, f"Turno de {turno.mascota.nombre} marcado como completado."
        )
        return redirect("turnos:agenda_vet")


class TurnoNoAsistioView(BaseTurnoAccionView):
    """Marcar que el cliente no asistió"""

    def post(self, request, pk):
        turno = self.get_turno(pk)

        if not turno.reservado:
            messages.error(
                request, "No se puede marcar como 'no asistió' un turno no reservado."
            )
            return redirect("turnos:agenda_vet")

        estado_no_asistio = EstadoTurno.objects.get(codigo=EstadoTurno.NO_ASISTIO)
        turno.estado = estado_no_asistio
        turno.save()

        messages.warning(
            request, f"Turno de {turno.mascota.nombre} marcado como 'No asistió'."
        )
        return redirect("turnos:agenda_vet")


class TurnosJSONView(LoginRequiredMixin, VeterinarioRequiredMixin, View):
    """Endpoint JSON para calendario del veterinario"""

    def get(self, request, *args, **kwargs):
        # Filtrar solo turnos reservados
        turnos = Turno.objects.filter(
            veterinario=request.user,
            reservado=True,
            cliente__isnull=False,
        ).select_related("estado", "mascota", "cliente")

        eventos = []

        for turno in turnos:
            start = timezone.datetime.combine(turno.fecha, turno.hora_inicio)
            end = timezone.datetime.combine(turno.fecha, turno.hora_fin)
            titulo = f"{turno.mascota.nombre} - {turno.cliente.get_full_name()}"

            eventos.append(
                {
                    "id": turno.id,
                    "title": titulo,
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "color": turno.estado.color if turno.estado else "#6c757d",
                    "extendedProps": {
                        "estado": turno.estado.nombre if turno.estado else "Sin estado",
                        "reservado": turno.reservado,
                        "mascota": turno.mascota.nombre if turno.mascota else "",
                        "cliente": (
                            turno.cliente.get_full_name() if turno.cliente else ""
                        ),
                    },
                }
            )

        return JsonResponse(eventos, safe=False)


# ==================== CLIENTE - TURNOS DISPONIBLES ====================


class TurnosDisponiblesListView(LoginRequiredMixin, ClienteRequiredMixin, ListView):
    """Lista de turnos disponibles para que el cliente reserve"""

    model = Turno
    template_name = "turnos/disponibles.html"
    context_object_name = "turnos"

    def get_queryset(self):
        queryset = (
            Turno.objects.filter(
                clinica=self.request.user.clinica,
                reservado=False,
                fecha__gte=timezone.now().date(),
            )
            .select_related("veterinario", "estado")
            .order_by("fecha", "hora_inicio")
        )

        # Filtro por veterinario
        veterinario_id = self.request.GET.get("veterinario")
        if veterinario_id:
            queryset = queryset.filter(veterinario_id=veterinario_id)

        # Filtro por fecha
        fecha = self.request.GET.get("fecha")
        if fecha:
            queryset = queryset.filter(fecha=fecha)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Veterinarios activos en la clínica
        context["veterinarios"] = CustomUser.objects.filter(
            rol="veterinario", clinica=self.request.user.clinica, is_active=True
        )

        # Mascotas activas del cliente
        context["mascotas"] = Mascota.objects.filter(
            dueno=self.request.user, activo=True
        )

        # Fechas con turnos disponibles
        fechas_queryset = Turno.objects.filter(
            clinica=self.request.user.clinica,
            reservado=False,
            fecha__gte=timezone.now().date(),
        )

        # Aplicar filtro de veterinario si existe
        veterinario_id = self.request.GET.get("veterinario")
        if veterinario_id:
            fechas_queryset = fechas_queryset.filter(veterinario_id=veterinario_id)

        # Obtener fechas únicas ordenadas
        context["fechas_disponibles"] = (
            fechas_queryset.values_list("fecha", flat=True).distinct().order_by("fecha")
        )

        return context


class TurnoReservarView(LoginRequiredMixin, ClienteRequiredMixin, View):
    """Reservar turno - Confirmación AUTOMÁTICA"""

    def post(self, request, pk):
        mascota_id = request.POST.get("mascota")
        motivo = request.POST.get("motivo", "")

        mascota = get_object_or_404(
            Mascota, id=mascota_id, dueno=request.user, activo=True
        )

        try:
            with transaction.atomic():
                turno = Turno.objects.select_for_update().get(pk=pk, reservado=False)
                turno.reservar(request.user, mascota)

                if motivo:
                    turno.motivo = motivo
                    turno.save()

            messages.success(
                request,
                f"✅ Turno reservado exitosamente para {mascota.nombre} el "
                f"{turno.fecha.strftime('%d/%m/%Y')} a las {turno.hora_inicio.strftime('%H:%M')}",
            )
        except Turno.DoesNotExist:
            messages.error(request, "El turno ya fue reservado por otro cliente.")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error al reservar: {str(e)}")

        return redirect("turnos:mis_turnos")


# ==================== CLIENTE - MIS TURNOS ====================


class MisTurnosListView(LoginRequiredMixin, ClienteRequiredMixin, ListView):
    """Lista de turnos del cliente"""

    model = Turno
    template_name = "turnos/mis_turnos.html"
    context_object_name = "turnos"

    def get_queryset(self):
        return (
            Turno.objects.filter(cliente=self.request.user)
            .select_related("veterinario", "estado", "mascota")
            .order_by("-fecha", "-hora_inicio")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.now().date()

        # Separar próximos y pasados
        context["turnos_proximos"] = self.get_queryset().filter(
            fecha__gte=timezone.now().date()
        )
        context["turnos_pasados"] = self.get_queryset().filter(
            fecha__lt=timezone.now().date()
        )

        return context


class TurnoDetalleClienteView(LoginRequiredMixin, DetailView):
    """Ver detalle de un turno (cliente)"""

    model = Turno
    template_name = "turnos/turno_detalle_cliente.html"
    context_object_name = "turno"

    def test_func(self):
        turno = self.get_object()
        return self.request.user == turno.cliente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.now().date()
        return context


class TurnoCancelarClienteView(LoginRequiredMixin, ClienteRequiredMixin, View):
    """Cancelar turno por cliente"""

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, cliente=request.user)

        # Obtener la hora actual en la zona horaria local
        ahora = timezone.localtime(timezone.now())

        # Crear datetime del turno en la zona horaria local
        datetime_turno_naive = datetime.combine(turno.fecha, turno.hora_inicio)
        datetime_turno = timezone.make_aware(datetime_turno_naive)
        datetime_turno_local = timezone.localtime(datetime_turno)

        horas_diferencia = (datetime_turno_local - ahora).total_seconds() / 3600

        if horas_diferencia < 2:
            messages.error(
                request,
                "No puedes cancelar turnos con menos de 2 horas de anticipación.",
            )
            return redirect("turnos:mis_turnos")

        if turno.estado.codigo == EstadoTurno.COMPLETADO:
            messages.error(request, "No puedes cancelar un turno completado.")
            return redirect("turnos:mis_turnos")

        turno.cancelar()
        messages.success(request, "Turno cancelado exitosamente.")

        return redirect("turnos:mis_turnos")


# ==================== ADMINISTRADOR - AGENDA CLÍNICA ====================


class AgendaClinicaView(LoginRequiredMixin, AdminVeterinariaRequiredMixin, ListView):
    """Agenda completa de la clínica (admin)"""

    model = Turno
    template_name = "turnos/agenda_clinica.html"
    context_object_name = "turnos"

    def get_queryset(self):
        return (
            Turno.objects.filter(
                clinica=self.request.user.clinica,
                reservado=True,
                fecha__gte=timezone.now().date(),
            )
            .select_related("veterinario", "estado", "cliente", "mascota")
            .order_by("fecha", "hora_inicio")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estados"] = EstadoTurno.objects.filter(activo=True)
        context["veterinarios"] = CustomUser.objects.filter(
            rol="veterinario", clinica=self.request.user.clinica, is_active=True
        )
        return context


class TurnoDetalleAdminView(LoginRequiredMixin, DetailView):
    """Ver detalle de un turno (admin)"""

    model = Turno
    template_name = "turnos/turno_detalle_admin.html"
    context_object_name = "turno"

    def test_func(self):
        turno = self.get_object()
        return self.request.user.clinica == turno.clinica


class TurnoCancelarAdminView(LoginRequiredMixin, AdminVeterinariaRequiredMixin, View):
    """Cancelar cualquier turno (admin)"""

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, clinica=request.user.clinica)
        motivo = request.POST.get("motivo", "Cancelado por administración")

        if turno.reservado:
            estado_cancelado = EstadoTurno.objects.get(codigo=EstadoTurno.CANCELADO)
            turno.estado = estado_cancelado
            turno.motivo_cancelacion = motivo
            turno.save()
            messages.success(
                request, f"Turno de {turno.cliente.get_full_name()} cancelado."
            )
        else:
            turno.delete()
            messages.success(request, "Turno disponible eliminado.")

        return redirect("turnos:agenda_clinica")


class TurnoCrearAdminView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, CreateView
):
    """Crear turno manual (admin) - Con búsqueda de cliente"""

    model = Turno
    form_class = TurnoCrearAdminForm
    template_name = "turnos/turno_crear_admin.html"
    success_url = reverse_lazy("turnos:agenda_clinica")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Obtener cliente y mascota de los campos ocultos
        cliente_id = form.cleaned_data["cliente_id"]
        mascota_id = form.cleaned_data["mascota_id"]

        try:
            cliente = CustomUser.objects.get(
                id=cliente_id, rol="cliente", clinica=self.request.user.clinica
            )
            mascota = Mascota.objects.get(id=mascota_id, dueno=cliente, activo=True)
        except (CustomUser.DoesNotExist, Mascota.DoesNotExist):
            form.add_error(None, "Cliente o mascota no válidos")
            return self.form_invalid(form)

        # Configurar el turno
        form.instance.clinica = self.request.user.clinica
        form.instance.creado_por = self.request.user
        form.instance.cliente = cliente
        form.instance.mascota = mascota
        form.instance.reservado = True
        form.instance.estado = EstadoTurno.objects.get(codigo=EstadoTurno.CONFIRMADO)

        # Validar solapamiento
        inicio = form.instance.hora_inicio
        fin = (
            timezone.datetime.combine(form.instance.fecha, inicio)
            + timezone.timedelta(minutes=form.instance.duracion_minutos)
        ).time()

        solapado = Turno.objects.filter(
            veterinario=form.instance.veterinario,
            fecha=form.instance.fecha,
            hora_inicio__lt=fin,
            hora_fin__gt=inicio,
        ).exists()

        if solapado:
            form.add_error(
                None, "El turno se solapa con otro existente para el veterinario."
            )
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Turno creado para {cliente.get_full_name()} - {mascota.nombre} el "
            f"{form.instance.fecha.strftime('%d/%m/%Y')} a las {inicio.strftime('%H:%M')}",
        )
        return super().form_valid(form)


class TurnosClinicaJSONView(LoginRequiredMixin, AdminVeterinariaRequiredMixin, View):
    """Endpoint JSON para calendario de toda la clínica"""

    def get(self, request, *args, **kwargs):
        clinica = request.user.clinica
        veterinario_id = request.GET.get("veterinario")
        estado_codigo = request.GET.get("estado")

        # Base queryset
        turnos = Turno.objects.filter(
            clinica=clinica, reservado=True, fecha__gte=timezone.now().date()
        )

        # Aplicar filtros
        if veterinario_id:
            turnos = turnos.filter(veterinario_id=veterinario_id)
        if estado_codigo:
            turnos = turnos.filter(estado__codigo=estado_codigo)

        turnos = turnos.select_related("veterinario", "estado", "mascota", "cliente")

        # Colores por veterinario
        colores = [
            "#007bff",
            "#28a745",
            "#ffc107",
            "#dc3545",
            "#6f42c1",
            "#20c997",
            "#e83e8c",
            "#17a2b8",
            "#6610f2",
            "#fd7e14",
        ]
        colores_por_vet = {}
        eventos = []

        for turno in turnos:
            vet_id = turno.veterinario.id
            if vet_id not in colores_por_vet:
                colores_por_vet[vet_id] = colores[len(colores_por_vet) % len(colores)]

            start = timezone.make_aware(
                timezone.datetime.combine(turno.fecha, turno.hora_inicio)
            )
            end = timezone.make_aware(
                timezone.datetime.combine(turno.fecha, turno.hora_fin)
            )

            titulo = f"{turno.veterinario.get_full_name()} - {turno.mascota.nombre}"

            eventos.append(
                {
                    "id": turno.id,
                    "title": titulo,
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "color": colores_por_vet[vet_id],
                    "extendedProps": {
                        "veterinario": turno.veterinario.get_full_name(),
                        "estado": turno.estado.nombre if turno.estado else "",
                        "cliente": turno.cliente.get_full_name(),
                        "mascota": turno.mascota.nombre,
                        "reservado": turno.reservado,
                    },
                }
            )

        return JsonResponse(eventos, safe=False)


# ==================== APIS PARA ADMIN ====================


class BuscarClientesAPIView(LoginRequiredMixin, AdminVeterinariaRequiredMixin, View):
    """API para buscar clientes y obtener sus mascotas"""

    def get(self, request):
        query = request.GET.get("q", "").strip()

        if len(query) < 2:
            return JsonResponse({"clientes": []})

        clientes = CustomUser.objects.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(username__icontains=query),
            rol="cliente",
            clinica=request.user.clinica,
            is_active=True,
        )[:10]

        resultados = []
        for cliente in clientes:
            mascotas = Mascota.objects.filter(
                dueno=cliente, activo=True
            ).select_related("raza", "especie")

            resultados.append(
                {
                    "id": cliente.id,
                    "nombre_completo": cliente.get_full_name(),
                    "email": cliente.email or "No registrado",
                    "telefono": getattr(cliente, "telefono", "No registrado"),
                    "mascotas": [
                        {
                            "id": m.id,
                            "nombre": m.nombre,
                            "especie": str(m.especie) if m.especie else "Sin especie",
                            "raza": str(m.raza) if m.raza else "Sin raza",
                        }
                        for m in mascotas
                    ],
                }
            )

        return JsonResponse({"clientes": resultados})


class MascotasPorClienteAPIView(
    LoginRequiredMixin, AdminVeterinariaRequiredMixin, View
):
    """API para obtener mascotas de un cliente específico"""

    def get(self, request, cliente_id):
        try:
            cliente = CustomUser.objects.get(
                id=cliente_id, rol="cliente", clinica=request.user.clinica
            )

            mascotas = Mascota.objects.filter(
                dueno=cliente, activo=True
            ).select_related("raza", "especie")

            return JsonResponse(
                {
                    "success": True,
                    "cliente": {
                        "id": cliente.id,
                        "nombre_completo": cliente.get_full_name(),
                        "email": cliente.email or "No registrado",
                        "telefono": getattr(cliente, "telefono", "No registrado"),
                    },
                    "mascotas": [
                        {
                            "id": m.id,
                            "nombre": m.nombre,
                            "especie": str(m.especie) if m.especie else "Sin especie",
                            "raza": str(m.raza) if m.raza else "Sin raza",
                        }
                        for m in mascotas
                    ],
                }
            )
        except CustomUser.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Cliente no encontrado"}, status=404
            )
