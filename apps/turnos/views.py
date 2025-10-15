from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, View
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

    def get_queryset(self):
        return DisponibilidadVeterinario.objects.filter(veterinario=self.request.user)


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


class TurnoReservarView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == "cliente"

    def post(self, request, pk):
        turno = get_object_or_404(Turno, pk=pk, reservado=False)
        mascota_id = request.POST.get("mascota")
        mascota = get_object_or_404(Mascota, id=mascota_id, dueno=request.user)

        try:
            turno.reservar(request.user, mascota)
            messages.success(request, "¡Turno reservado exitosamente!")
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
        return Turno.objects.filter(cliente=self.request.user).order_by("-fecha")


class AgendaVeterinarioView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Turno
    template_name = "turnos/agenda_veterinario.html"
    context_object_name = "turnos"

    def test_func(self):
        return self.request.user.rol == "veterinario"

    def get_queryset(self):
        return Turno.objects.filter(
            veterinario=self.request.user, fecha__gte=timezone.now().date()
        )


# Endpoint para el calendario (datos JSON)
class TurnosJSONView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == "veterinario"

    def get(self, request, *args, **kwargs):
        turnos = Turno.objects.filter(veterinario=request.user).select_related(
            "estado", "mascota"
        )
        eventos = []

        for turno in turnos:
            start = timezone.datetime.combine(turno.fecha, turno.hora_inicio)
            end = timezone.datetime.combine(turno.fecha, turno.hora_fin)
            eventos.append(
                {
                    "id": turno.id,
                    "title": f"{turno.mascota.nombre if turno.mascota else 'Disponible'}",
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


# Admin Clinica
class AgendaClinicaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Turno
    template_name = "turnos/agenda_clinica.html"
    context_object_name = "turnos"

    def test_func(self):
        return self.request.user.rol == "admin_clinica"

    def get_queryset(self):
        return Turno.objects.filter(
            clinica=self.request.user.clinica, fecha__gte=timezone.now().date()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estados"] = EstadoTurno.objects.filter(activo=True)
        return context


# Endpoint JSON: turnos de todos los veterinarios de la clínica
class TurnosClinicaJSONView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == "admin_clinica"

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

        for i, turno in enumerate(turnos):
            vet = turno.veterinario
            if vet not in colores_por_vet:
                colores_por_vet[vet] = colores[i % len(colores)]

            start = timezone.datetime.combine(turno.fecha, turno.hora_inicio)
            end = timezone.datetime.combine(turno.fecha, turno.hora_fin)
            eventos.append(
                {
                    "id": turno.id,
                    "title": f"{vet.nombre_completo} - {turno.mascota.nombre if turno.mascota else 'Disponible'}",
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "color": colores_por_vet[vet],
                    "extendedProps": {
                        "veterinario": vet.nombre_completo,
                        "estado": turno.estado.nombre if turno.estado else "",
                        "cliente": (
                            turno.cliente.nombre_completo if turno.cliente else ""
                        ),
                        "mascota": turno.mascota.nombre if turno.mascota else "",
                    },
                }
            )
        return JsonResponse(eventos, safe=False)
