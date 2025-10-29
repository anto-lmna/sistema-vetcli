from datetime import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import PerfilCliente
from apps.clinicas.models import Clinica
from apps.accounts.models import CustomUser

User = get_user_model()


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.admin_vet = CustomUser.objects.create_user(
            username="adminvet",
            email="adminvet@test.com",
            password="12345",
            rol="admin_veterinaria",
        )

        self.clinica = Clinica.objects.create(
            nombre="Clinica San Vet",
            email="sanvet@test.com",
            telefono="123456789",
            direccion="Av. Siempre Viva 123",
            hora_apertura=time(8, 0),
            hora_cierre=time(18, 0),
            admin=self.admin_vet,
        )

    def test_crear_admin_veterinaria(self):
        """Debe crear un usuario con rol admin_veterinaria sin perfil asociado"""
        admin = User.objects.create_user(
            username="admin1",
            email="admin@test.com",
            password="pass1234",
            rol="admin_veterinaria",
            clinica=self.clinica,
            first_name="Ana",
            last_name="Perez",
        )
        self.assertTrue(admin.is_admin_veterinaria)
        self.assertFalse(admin.is_veterinario)
        self.assertFalse(admin.is_cliente)
        self.assertEqual(str(admin), "Ana Perez (Administrador Veterinaria)")
        self.assertEqual(admin.clinica, self.clinica)
        self.assertFalse(hasattr(admin, "perfilcliente"))
        self.assertFalse(hasattr(admin, "perfilveterinario"))

    def test_crear_veterinario(self):
        """Debe crear un veterinario y NO generar perfil automáticamente"""
        vet = User.objects.create_user(
            username="vet1",
            email="vet@test.com",
            password="pass1234",
            rol="veterinario",
            clinica=self.clinica,
            first_name="Carlos",
            last_name="Lopez",
        )
        self.assertTrue(vet.is_veterinario)
        self.assertFalse(vet.is_admin_veterinaria)
        self.assertFalse(vet.is_cliente)
        # Perfil no se crea automáticamente
        self.assertFalse(hasattr(vet, "perfilveterinario"))

    def test_crear_cliente_crea_perfil_automatico(self):
        """Debe crear un cliente y generarse su perfil automáticamente"""
        cliente = User.objects.create_user(
            username="cliente1",
            email="cliente@test.com",
            password="pass1234",
            rol="cliente",
            clinica=self.clinica,
            first_name="Laura",
            last_name="Gomez",
        )
        self.assertTrue(cliente.is_cliente)
        self.assertFalse(cliente.is_veterinario)
        self.assertFalse(cliente.is_admin_veterinaria)

        self.assertTrue(hasattr(cliente, "perfilcliente"))
        self.assertIsInstance(cliente.perfilcliente, PerfilCliente)
        self.assertEqual(cliente.perfilcliente.user, cliente)

    def test_dashboard_urls(self):
        """Debe devolver la URL correcta según el rol"""
        admin = User(rol="admin_veterinaria")
        vet = User(rol="veterinario")
        cliente = User(rol="cliente")

        self.assertEqual(admin.dashboard_url, "/dashboard/admin/")
        self.assertEqual(vet.dashboard_url, "/dashboard/veterinario/")
        self.assertEqual(cliente.dashboard_url, "/dashboard/cliente/")
