from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from apps.mascotas.models import Mascota
from .models import Turno, DisponibilidadVeterinario, EstadoTurno


# Veterinario
class DisponibilidadListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DisponibilidadVeterinario
    template_name = "turnos/disponibilidad_list.html"
    context_object_name = "disponibilidades"

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.now().date()
        return context

    def get_queryset(self):
        return DisponibilidadVeterinario.objects.filter(
            veterinario=self.request.user
        ).order_by("-fecha")


class DisponibilidadCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = DisponibilidadVeterinario
    fields = ["fecha", "hora_inicio", "hora_fin", "duracion_turno"]
    template_name = "turnos/disponibilidad_form.html"
    success_url = reverse_lazy("turnos:disponibilidades")

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def form_valid(self, form):
        form.instance.veterinario = self.request.user
        form.instance.clinica = self.request.user.clinica
        response = super().form_valid(form)
        form.instance.generar_turnos()
        messages.success(self.request, "Disponibilidad creada y turnos generados.")
        return response


class DisponibilidadDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Eliminar disponibilidad (y sus turnos no reservados)"""

    model = DisponibilidadVeterinario
    template_name = "turnos/disponibilidad_confirm_delete.html"
    success_url = reverse_lazy("turnos:disponibilidades")

    def test_func(self):
        disp = self.get_object()
        return self.request.user == disp.veterinario

    def delete(self, request, *args, **kwargs):
        disp = self.get_object()
        # Contar turnos reservados
        turnos_reservados = Turno.objects.filter(
            veterinario=disp.veterinario,
            fecha=disp.fecha,
            hora_inicio__gte=disp.hora_inicio,
            hora_inicio__lt=disp.hora_fin,
            reservado=True,
        ).count()

        if turnos_reservados > 0:
            messages.error(
                request,
                f"No se puede eliminar. Hay {turnos_reservados} turno(s) ya reservado(s) en este horario.",
            )
            return redirect("turnos:disponibilidades")

        # Eliminar solo turnos no reservados
        turnos_eliminados = Turno.objects.filter(
            veterinario=disp.veterinario,
            fecha=disp.fecha,
            hora_inicio__gte=disp.hora_inicio,
            hora_inicio__lt=disp.hora_fin,
            reservado=False,
        ).delete()[0]

        messages.success(
            request,
            f"Disponibilidad eliminada. {turnos_eliminados} turno(s) disponible(s) eliminado(s).",
        )
        return super().delete(request, *args, **kwargs)


class AgendaVeterinarioView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Turno
    template_name = "turnos/agenda_veterinario.html"
    context_object_name = "turnos"

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def get_queryset(self):
        return (
            Turno.objects.filter(
                veterinario=self.request.user, fecha__gte=timezone.now().date()
            )
            .select_related("estado", "cliente", "mascota")
            .order_by("fecha", "hora_inicio")
        )


class TurnoDetalleVeterinarioView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Ver detalle de un turno (veterinario)"""

    model = Turno
    template_name = "turnos/turno_detalle_veterinario.html"
    context_object_name = "turno"

    def test_func(self):
        turno = self.get_object()
        return self.request.user == turno.veterinario


class TurnoIniciarAtencionView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Marcar turno como 'En curso'"""

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, veterinario=request.user)

        if not turno.reservado:
            messages.error(
                request, "No se puede iniciar atención de un turno no reservado."
            )
            return redirect("turnos:agenda_vet")

        estado_en_curso = EstadoTurno.objects.get(codigo=EstadoTurno.EN_CURSO)
        turno.estado = estado_en_curso
        turno.save()

        messages.info(request, f"Atención de {turno.mascota.nombre} iniciada.")
        return redirect("turnos:turno_detalle_vet", pk=pk)


class TurnoCompletarView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Marcar turno como completado"""

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, veterinario=request.user)

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


class TurnoNoAsistioView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Marcar que el cliente no asistió"""

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, veterinario=request.user)

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


class TurnosJSONView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Endpoint JSON para calendario del veterinario"""

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def get(self, request, *args, **kwargs):
        turnos = Turno.objects.filter(veterinario=request.user).select_related(
            "estado", "mascota", "cliente"
        )
        eventos = []

        for turno in turnos:
            start = timezone.datetime.combine(turno.fecha, turno.hora_inicio)
            end = timezone.datetime.combine(turno.fecha, turno.hora_fin)

            # Título según si está reservado o no
            if turno.reservado and turno.mascota:
                titulo = f"{turno.mascota.nombre} - {turno.cliente.nombre_completo}"
            else:
                titulo = "Disponible"

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
                            turno.cliente.nombre_completo if turno.cliente else ""
                        ),
                    },
                }
            )
        return JsonResponse(eventos, safe=False)


# Cliente
class TurnosDisponiblesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Turno
    template_name = "turnos/disponibles.html"
    context_object_name = "turnos"

    def test_func(self):
        return self.request.user.rol == "cliente"

    def get_queryset(self):
        return (
            Turno.objects.filter(
                clinica=self.request.user.clinica,
                reservado=False,
                fecha__gte=timezone.now().date(),
            )
            .select_related("veterinario", "estado")
            .order_by("fecha", "hora_inicio")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar mascotas del cliente para el formulario de reserva
        context["mascotas"] = Mascota.objects.filter(
            dueno=self.request.user, activo=True
        )
        return context


class TurnoReservarView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Reservar turno (confirmación automática)"""

    def test_func(self):
        return self.request.user.rol == "cliente"

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, reservado=False)
        mascota_id = request.POST.get("mascota")
        motivo = request.POST.get("motivo", "")

        mascota = get_object_or_404(
            Mascota, id=mascota_id, dueno=request.user, activo=True
        )

        try:
            # Reservar turno (ya pasa a confirmado automáticamente)
            turno.reservar(request.user, mascota)

            # Guardar motivo si lo proporcionó
            if motivo:
                turno.motivo = motivo
                turno.save()

            messages.success(
                request,
                f"¡Turno reservado exitosamente para {mascota.nombre}! "
                f"Fecha: {turno.fecha.strftime('%d/%m/%Y')} a las {turno.hora_inicio.strftime('%H:%M')}",
            )
        except ValueError as e:
            messages.error(request, str(e))

        return redirect("turnos:mis_turnos")


class MisTurnosListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Turno
    template_name = "turnos/mis_turnos.html"
    context_object_name = "turnos"

    def test_func(self):
        return self.request.user.rol == "cliente"

    def get_queryset(self):
        return (
            Turno.objects.filter(cliente=self.request.user)
            .select_related("veterinario", "estado", "mascota")
            .order_by("-fecha", "-hora_inicio")
        )


class TurnoDetalleClienteView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Ver detalle de un turno (cliente)"""

    model = Turno
    template_name = "turnos/turno_detalle_cliente.html"
    context_object_name = "turno"

    def test_func(self):
        turno = self.get_object()
        return self.request.user == turno.cliente


class TurnoCancelarClienteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Cancelar turno (cliente)"""

    def test_func(self):
        return self.request.user.rol == "cliente"

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, cliente=request.user)

        # Validar que el turno sea futuro (al menos 2 horas antes)
        fecha_hora_turno = timezone.datetime.combine(turno.fecha, turno.hora_inicio)
        fecha_hora_turno = timezone.make_aware(fecha_hora_turno)
        ahora = timezone.now()

        # Mínimo 2 horas de anticipación
        from datetime import timedelta

        if fecha_hora_turno - ahora < timedelta(hours=2):
            messages.error(
                request,
                "No se puede cancelar con menos de 2 horas de anticipación. "
                "Por favor, contacta a la clínica.",
            )
            return redirect("turnos:mis_turnos")

        # Validar que no esté ya completado o en curso
        if turno.estado.codigo in [EstadoTurno.COMPLETADO, EstadoTurno.EN_CURSO]:
            messages.error(
                request, f"No se puede cancelar un turno {turno.estado.nombre.lower()}."
            )
            return redirect("turnos:mis_turnos")

        # Cancelar y liberar el turno
        estado_pendiente = EstadoTurno.objects.get(codigo=EstadoTurno.PENDIENTE)
        turno.estado = estado_pendiente
        turno.reservado = False
        turno.cliente = None
        turno.mascota = None
        turno.motivo = ""
        turno.save()

        messages.success(
            request, "Turno cancelado. El horario queda disponible nuevamente."
        )
        return redirect("turnos:mis_turnos")


# Administrador


class AgendaClinicaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Turno
    template_name = "turnos/agenda_clinica.html"
    context_object_name = "turnos"

    def test_func(self):
        return self.request.user.rol == "admin_veterinaria"

    def get_queryset(self):
        return (
            Turno.objects.filter(
                clinica=self.request.user.clinica, fecha__gte=timezone.now().date()
            )
            .select_related("veterinario", "estado", "cliente", "mascota")
            .order_by("fecha", "hora_inicio")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estados"] = EstadoTurno.objects.filter(activo=True)
        from apps.accounts.models import CustomUser

        context["veterinarios"] = CustomUser.objects.filter(
            rol="veterinario", clinica=self.request.user.clinica, is_active=True
        )
        return context


class TurnoDetalleAdminView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Ver detalle de un turno (admin)"""

    model = Turno
    template_name = "turnos/turno_detalle_admin.html"
    context_object_name = "turno"

    def test_func(self):
        turno = self.get_object()
        return self.request.user.clinica == turno.clinica


class TurnoCancelarAdminView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Cancelar cualquier turno (admin)"""

    def test_func(self):
        return self.request.user.rol == "admin_veterinaria"

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, clinica=request.user.clinica)
        motivo = request.POST.get("motivo", "Cancelado por administración")

        # Si estaba reservado, cancelar
        if turno.reservado:
            estado_cancelado = EstadoTurno.objects.get(codigo=EstadoTurno.CANCELADO)
            turno.estado = estado_cancelado
            turno.motivo_cancelacion = motivo
            turno.save()
            messages.success(
                request, f"Turno de {turno.cliente.nombre_completo} cancelado."
            )
        else:
            # Si no estaba reservado, simplemente eliminarlo
            turno.delete()
            messages.success(request, "Turno disponible eliminado.")

        return redirect("turnos:agenda_clinica")


class TurnoCrearAdminView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Crear turno manual (admin) - Para agendar por teléfono"""

    model = Turno
    template_name = "turnos/turno_crear_admin.html"
    fields = [
        "veterinario",
        "cliente",
        "mascota",
        "fecha",
        "hora_inicio",
        "duracion_minutos",
        "tipo_consulta",
        "motivo",
    ]
    success_url = reverse_lazy("turnos:agenda_clinica")

    def test_func(self):
        return self.request.user.rol == "admin_veterinaria"

    def form_valid(self, form):
        form.instance.clinica = self.request.user.clinica
        form.instance.creado_por = self.request.user
        form.instance.reservado = True

        # Estado confirmado automáticamente
        estado_confirmado = EstadoTurno.objects.get(codigo=EstadoTurno.CONFIRMADO)
        form.instance.estado = estado_confirmado

        messages.success(
            self.request,
            f"Turno creado para {form.instance.cliente.nombre_completo} "
            f"el {form.instance.fecha.strftime('%d/%m/%Y')} a las {form.instance.hora_inicio.strftime('%H:%M')}",
        )
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        from apps.accounts.models import CustomUser

        # Filtrar por clínica
        form.fields["veterinario"].queryset = CustomUser.objects.filter(
            rol="veterinario", clinica=self.request.user.clinica, is_active=True
        )
        form.fields["cliente"].queryset = CustomUser.objects.filter(
            rol="cliente", clinica=self.request.user.clinica, is_active=True
        )

        # Widgets mejorados
        form.fields["fecha"].widget.attrs.update(
            {"type": "date", "class": "form-control"}
        )
        form.fields["hora_inicio"].widget.attrs.update(
            {"type": "time", "class": "form-control"}
        )
        form.fields["duracion_minutos"].widget.attrs.update({"class": "form-control"})
        form.fields["tipo_consulta"].widget.attrs.update({"class": "form-select"})
        form.fields["motivo"].widget.attrs.update({"class": "form-control", "rows": 3})

        return form


class TurnosClinicaJSONView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Endpoint JSON para calendario de toda la clínica"""

    def test_func(self):
        return self.request.user.rol == "admin_veterinaria"

    def get(self, request, *args, **kwargs):
        clinica = request.user.clinica
        veterinario_id = request.GET.get("veterinario")
        estado_codigo = request.GET.get("estado")

        turnos = Turno.objects.filter(clinica=clinica, fecha__gte=timezone.now().date())

        if veterinario_id:
            turnos = turnos.filter(veterinario_id=veterinario_id)
        if estado_codigo:
            turnos = turnos.filter(estado__codigo=estado_codigo)

        turnos = turnos.select_related("veterinario", "estado", "mascota", "cliente")

        # Paleta de colores por veterinario
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
            vet = turno.veterinario
            if vet not in colores_por_vet:
                colores_por_vet[vet] = colores[len(colores_por_vet) % len(colores)]

            start = timezone.datetime.combine(turno.fecha, turno.hora_inicio)
            end = timezone.datetime.combine(turno.fecha, turno.hora_fin)

            # Título según si está reservado
            if turno.reservado and turno.mascota:
                titulo = f"{vet.nombre_completo} - {turno.mascota.nombre}"
            else:
                titulo = f"{vet.nombre_completo} - Disponible"

            eventos.append(
                {
                    "id": turno.id,
                    "title": titulo,
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "color": colores_por_vet[vet],
                    "extendedProps": {
                        "veterinario": vet.nombre_completo,
                        "estado": turno.estado.nombre if turno.estado else "",
                        "cliente": (
                            turno.cliente.nombre_completo
                            if turno.cliente
                            else "Disponible"
                        ),
                        "mascota": turno.mascota.nombre if turno.mascota else "",
                        "reservado": turno.reservado,
                    },
                }
            )
        return JsonResponse(eventos, safe=False)
