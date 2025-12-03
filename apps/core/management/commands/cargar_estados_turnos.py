from django.core.management.base import BaseCommand
from apps.turnos.models import EstadoTurno


class Command(BaseCommand):
    help = "Carga los estados de turno iniciales"

    def handle(self, *args, **kwargs):
        self.stdout.write("Cargando estados de turno...")

        estados = estados = [
            {
                "nombre": "Pendiente",
                "codigo": EstadoTurno.PENDIENTE,
                "color": "#CBD5E0",  # Gris Hielo (Neutral/En espera)
            },
            {
                "nombre": "Confirmado",
                "codigo": EstadoTurno.CONFIRMADO,
                "color": "#38B2AC",  # Verde Agua / Teal (Tu color de acento)
            },
            {
                "nombre": "En curso",
                "codigo": EstadoTurno.EN_CURSO,
                "color": "#805AD5",  # Violeta Vibrante (Tu color principal)
            },
            {
                "nombre": "Completado",
                "codigo": EstadoTurno.COMPLETADO,
                "color": "#48BB78",  # Verde Esmeralda Suave (Éxito)
            },
            {
                "nombre": "Cancelado",
                "codigo": EstadoTurno.CANCELADO,
                "color": "#FC8181",  # Rojo Rosado Suave (No agresivo)
            },
            {
                "nombre": "No asistió",
                "codigo": EstadoTurno.NO_ASISTIO,
                "color": "#718096",  # Gris Pizarra (Estado final neutral)
            },
        ]

        for estado_data in estados:
            estado, created = EstadoTurno.objects.get_or_create(
                codigo=estado_data["codigo"], defaults=estado_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Estado "{estado.nombre}" creado')
                )
            else:
                # Actualizar color si ya existe
                estado.color = estado_data["color"]
                estado.nombre = estado_data["nombre"]
                estado.save()
                self.stdout.write(
                    self.style.WARNING(f'• Estado "{estado.nombre}" actualizado')
                )

        self.stdout.write(self.style.SUCCESS("\n✅ Estados de turno cargados"))
