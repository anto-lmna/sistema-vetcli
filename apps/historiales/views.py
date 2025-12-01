from django.db import transaction
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView
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

        # Recuperamos la mascota de la URL (ej: /mascotas/5/historia/nueva/)
        # Esto asume que pasas el ID de la mascota en la URL
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

    # apps/historiales/views.py

    def form_valid(self, form):
        context = self.get_context_data()
        vacunas = context["vacunas"]
        archivos = context["archivos"]

        mascota = get_object_or_404(Mascota, pk=self.kwargs["mascota_id"])

        with transaction.atomic():
            # 1. Configurar y guardar la Historia Clínica (Padre)
            form.instance.mascota = mascota
            form.instance.clinica = self.request.user.clinica
            form.instance.veterinario = self.request.user
            self.object = form.save()

            # 2. Guardar VACUNAS (Aquí estaba el error)
            if vacunas.is_valid():
                vacunas.instance = self.object

                # TRUCO: Usamos commit=False para no guardar todavía en la BD
                vacunas_instances = vacunas.save(commit=False)

                for vacuna in vacunas_instances:
                    # Asignamos la mascota manualmente a cada vacuna
                    vacuna.mascota = mascota
                    vacuna.save()  # Ahora sí guardamos

                # Esto es necesario para guardar relaciones ManyToMany si las hubiera (no es tu caso, pero es buena práctica)
                # vacunas.save_m2m()

            # 3. Guardar ARCHIVOS
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
