from django.views.generic import DetailView
from .models import Clinica


class ClinicaDetailView(DetailView):
    model = Clinica
    template_name = "clinicas/detalle.html"
    context_object_name = "clinica"
    slug_field = "slug"
    slug_url_kwarg = "slug"
