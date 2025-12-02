from django.db import transaction
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import HistoriaClinica
from apps.mascotas.models import Mascota
from .forms import HistoriaClinicaForm, VacunaFormSet, ArchivoAdjuntoFormSet


class HistoriaClinicaCreateView(LoginRequiredMixin, CreateView):
    model = HistoriaClinica
    form_class = HistoriaClinicaForm
    template_name = "historias/historia_form.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        # Recuperamos la mascota de la URL
        if self.request.POST:
            data["vacunas"] = VacunaFormSet(self.request.POST)
            data["archivos"] = ArchivoAdjuntoFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            data["vacunas"] = VacunaFormSet()
            data["archivos"] = ArchivoAdjuntoFormSet()

        # Pasamos datos extra para el template
        data["mascota"] = get_object_or_404(Mascota, pk=self.kwargs["mascota_id"])
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        vacunas = context["vacunas"]
        archivos = context["archivos"]

        mascota = get_object_or_404(Mascota, pk=self.kwargs["mascota_id"])

        with transaction.atomic():
            form.instance.mascota = mascota
            form.instance.clinica = self.request.user.clinica
            form.instance.veterinario = self.request.user
            self.object = form.save()

            turno_id = self.request.GET.get("turno_id")
            if turno_id:
                try:
                    # Importamos aquí para evitar referencias circulares
                    from apps.turnos.models import Turno, EstadoTurno

                    turno = Turno.objects.get(
                        pk=turno_id, veterinario=self.request.user
                    )

                    # Opcional: Vincular historia con turno en BD si tienes el campo
                    form.instance.turno = turno
                    form.instance.save()

                    # COMPLETAR EL TURNO AUTOMÁTICAMENTE
                    estado_completado = EstadoTurno.objects.get(
                        codigo=EstadoTurno.COMPLETADO
                    )
                    turno.estado = estado_completado
                    turno.save()

                    messages.success(
                        self.request,
                        "Consulta guardada y turno marcado como COMPLETADO.",
                    )
                except Turno.DoesNotExist:
                    pass
            if vacunas.is_valid():
                vacunas.instance = self.object

                vacunas_instances = vacunas.save(commit=False)

                for vacuna in vacunas_instances:
                    vacuna.mascota = mascota
                    vacuna.save()

            if archivos.is_valid():
                archivos.instance = self.object
                archivos.save()

        return super().form_valid(form)

    def get_success_url(self):
        # Redirigir al perfil de la mascota tras guardar
        return reverse(
            "mascotas:detalle_mascota", kwargs={"pk": self.kwargs["mascota_id"]}
        )


class HistoriaDetailView(LoginRequiredMixin, DetailView):
    model = HistoriaClinica
    template_name = "historias/historia_detalle.html"
    context_object_name = "historia"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadimos datos extra si los necesitas
        context["titulo"] = f"Historia Clínica - {self.object.mascota.nombre}"
        return context
