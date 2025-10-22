from datetime import time, date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.clinicas.models import Clinica

User = get_user_model()


class Command(BaseCommand):
    help = "Crea datos de prueba para el sistema"

    def handle(self, *args, **options):
        self.stdout.write("Creando datos de prueba...")

        # 1. Crear usuario administrador de veterinaria
        if not User.objects.filter(username="admin_vet").exists():
            admin_user = User.objects.create_user(
                username="admin_vet",
                email="admin@veterinaria.com",
                password="admin123",
                first_name="Juan",
                last_name="Pérez",
                rol="admin_veterinaria",
                dni="12345678",
                telefono="011-1234-5678",
                is_active=True,
            )
            self.stdout.write(f"✅ Creado admin: {admin_user.username}")
        else:
            admin_user = User.objects.get(username="admin_vet")
            self.stdout.write(f"ℹ️  Admin ya existe: {admin_user.username}")

        # 2. Crear clínica veterinaria
        if not Clinica.objects.filter(slug="veterinaria-central").exists():
            clinica = Clinica.objects.create(
                nombre="Veterinaria Central",
                descripcion="La mejor atención veterinaria para tus mascotas",
                direccion="Av. Corrientes 1234, Buenos Aires",
                telefono="011-4567-8901",
                email="info@veterinariacentral.com",
                admin=admin_user,  # Usar el campo admin
                hora_apertura=time(9, 0),
                hora_cierre=time(18, 0),
                dias_atencion=[
                    "lunes",
                    "martes",
                    "miércoles",
                    "jueves",
                    "viernes",
                    "sábado",
                ],
                is_active=True,
                acepta_nuevos_clientes=True,
                slug="veterinaria-central",
            )
            self.stdout.write(f"✅ Creada clínica: {clinica.nombre}")
        else:
            clinica = Clinica.objects.get(slug="veterinaria-central")
            self.stdout.write(f"ℹ️  Clínica ya existe: {clinica.nombre}")

        # Asignar clínica al admin también (para consistencia)
        admin_user.clinica = clinica
        admin_user.save()

        # 3. Crear veterinario
        if not User.objects.filter(username="dr_lopez").exists():
            vet_user = User.objects.create_user(
                username="dr_lopez",
                email="lopez@veterinaria.com",
                password="vet123",
                first_name="María",
                last_name="López",
                rol="veterinario",
                dni="87654321",
                telefono="011-9876-5432",
                direccion="Av. Siempre Viva 742",
                fecha_nacimiento=date(1987, 7, 9),
                is_active=True,
                clinica=clinica,
            )

            # El perfil se crea automáticamente por la señal, solo actualizamos
            vet_user.perfilveterinario.matricula = "VET-001"
            vet_user.perfilveterinario.especialidad = "Medicina General"
            vet_user.perfilveterinario.experiencia_anos = 5
            vet_user.perfilveterinario.save()

            self.stdout.write(f"✅ Creado veterinario: {vet_user.username}")
        else:
            self.stdout.write("ℹ️  Veterinario ya existe: dr_lopez")

        # 4. Crear cliente activo
        if not User.objects.filter(username="cliente_activo").exists():
            cliente_user = User.objects.create_user(
                username="cliente_activo",
                email="cliente@gmail.com",
                password="cliente123",
                first_name="Ana",
                last_name="García",
                rol="cliente",
                dni="11223344",
                fecha_nacimiento=date(1984, 3, 14),
                telefono="011-1111-2222",
                direccion="Malabia 1565",
                is_active=True,
                pendiente_aprobacion=False,
                clinica=clinica,
            )

            # El perfil se crea automáticamente, solo actualizamos
            cliente_user.perfilcliente.contacto_emergencia = "Pedro García"
            cliente_user.perfilcliente.telefono_emergencia = "011-3333-4444"
            cliente_user.perfilcliente.save()

            self.stdout.write(f"✅ Creado cliente activo: {cliente_user.username}")
        else:
            self.stdout.write("ℹ️  Cliente activo ya existe: cliente_activo")

        # 5. Crear cliente pendiente
        if not User.objects.filter(username="cliente_pendiente").exists():
            cliente_pendiente = User.objects.create_user(
                username="cliente_pendiente",
                email="pendiente@gmail.com",
                password="pendiente123",
                first_name="Carlos",
                last_name="Rodríguez",
                rol="cliente",
                dni="44556677",
                fecha_nacimiento=date(1992, 1, 23),
                telefono="011-5555-6666",
                direccion="Guatemala 4567",
                is_active=False,
                pendiente_aprobacion=True,
                clinica=clinica,
            )

            # El perfil se crea automáticamente, solo actualizamos
            cliente_pendiente.perfilcliente.contacto_emergencia = "Luis Rodríguez"
            cliente_pendiente.perfilcliente.telefono_emergencia = "011-7777-8888"
            cliente_pendiente.perfilcliente.save()

            self.stdout.write(
                f"✅ Creado cliente pendiente: {cliente_pendiente.username}"
            )
        else:
            self.stdout.write("ℹ️  Cliente pendiente ya existe: cliente_pendiente")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("🎉 DATOS DE PRUEBA CREADOS EXITOSAMENTE"))
        self.stdout.write("=" * 50)
        self.stdout.write("\n📋 CREDENCIALES DE ACCESO:")
        self.stdout.write(f"👨‍💼 Admin: admin_vet / admin123")
        self.stdout.write(f"👨‍⚕️ Veterinario: dr_lopez / vet123")
        self.stdout.write(f"👤 Cliente Activo: cliente_activo / cliente123")
        self.stdout.write(f"⏳ Cliente Pendiente: cliente_pendiente / pendiente123")
        self.stdout.write("\n🌐 URLs importantes:")
        self.stdout.write("• Home: http://127.0.0.1:8000/")
        self.stdout.write("• Login: http://127.0.0.1:8000/accounts/login/")
        self.stdout.write("• Admin: http://127.0.0.1:8000/admin/")
        self.stdout.write("=" * 50)
