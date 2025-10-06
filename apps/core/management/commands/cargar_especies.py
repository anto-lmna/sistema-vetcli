from django.core.management.base import BaseCommand
from apps.mascotas.models import Especie, Raza


class Command(BaseCommand):
    help = "Carga especies y razas iniciales"

    def handle(self, *args, **kwargs):
        self.stdout.write("Cargando especies y razas...")

        # Crear especies
        perro, _ = Especie.objects.get_or_create(
            nombre="Perro", defaults={"descripcion": "Canis lupus familiaris"}
        )

        gato, _ = Especie.objects.get_or_create(
            nombre="Gato", defaults={"descripcion": "Felis catus"}
        )

        # Razas de perros
        razas_perros = [
            "Labrador Retriever",
            "Golden Retriever",
            "Pastor Alemán",
            "Bulldog",
            "Beagle",
            "Poodle",
            "Rottweiler",
            "Yorkshire Terrier",
            "Boxer",
            "Dachshund",
            "Chihuahua",
            "Mestizo",
        ]

        for raza_nombre in razas_perros:
            Raza.objects.get_or_create(nombre=raza_nombre, especie=perro)

        # Razas de gatos
        razas_gatos = [
            "Siamés",
            "Persa",
            "Maine Coon",
            "Bengalí",
            "Ragdoll",
            "British Shorthair",
            "Sphynx",
            "Mestizo",
        ]

        for raza_nombre in razas_gatos:
            Raza.objects.get_or_create(nombre=raza_nombre, especie=gato)

        self.stdout.write(self.style.SUCCESS("✓ Especies y razas cargadas"))
