from django.core.management.base import BaseCommand
from apps.turnos.models import EstadoTurno


class Command(BaseCommand):
    help = "Carga los estados de turno iniciales"

    def handle(self, *args, **kwargs):
        self.stdout.write("Cargando estados de turno...")

        estados = [
            {
                "nombre": "Pendiente",
                "codigo": EstadoTurno.PENDIENTE,
                "color": "#ffc107",  # Amarillo
            },
            {
                "nombre": "Confirmado",
                "codigo": EstadoTurno.CONFIRMADO,
                "color": "#0dcaf0",  # Cyan
            },
            {
                "nombre": "En curso",
                "codigo": EstadoTurno.EN_CURSO,
                "color": "#0d6efd",  # Azul
            },
            {
                "nombre": "Completado",
                "codigo": EstadoTurno.COMPLETADO,
                "color": "#198754",  # Verde
            },
            {
                "nombre": "Cancelado",
                "codigo": EstadoTurno.CANCELADO,
                "color": "#dc3545",  # Rojo
            },
            {
                "nombre": "No asistió",
                "codigo": EstadoTurno.NO_ASISTIO,
                "color": "#6c757d",  # Gris
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
