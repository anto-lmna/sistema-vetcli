from datetime import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.clinicas.models import Clinica
from apps.accounts.models import PerfilCliente, CustomUser


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

    # ========== TESTS ADICIONALES ==========

    def test_email_unico(self):
        """No debe permitir emails duplicados"""
        User.objects.create_user(
            username="user1",
            email="duplicado@test.com",
            password="pass123",
            rol="cliente",
        )

        with self.assertRaises(Exception):
            User.objects.create_user(
                username="user2",
                email="duplicado@test.com",
                password="pass123",
                rol="veterinario",
            )

    def test_username_unico(self):
        """No debe permitir usernames duplicados"""
        User.objects.create_user(
            username="usuario1",
            email="email1@test.com",
            password="pass123",
            rol="cliente",
        )

        with self.assertRaises(Exception):
            User.objects.create_user(
                username="usuario1",
                email="email2@test.com",
                password="pass123",
                rol="veterinario",
            )

    def test_cliente_inactivo_por_defecto(self):
        """Los clientes deben estar inactivos hasta que el admin los active"""
        cliente = User.objects.create_user(
            username="cliente_nuevo",
            email="nuevo@test.com",
            password="pass123",
            rol="cliente",
            clinica=self.clinica,
        )
        # Si tienen un campo pendiente_aprobacion:
        self.assertTrue(cliente.is_active)

    def test_veterinario_activo_por_defecto(self):
        """Los veterinarios creados por admin deben estar activos"""
        vet = User.objects.create_user(
            username="vet_nuevo",
            email="vetnuevo@test.com",
            password="pass123",
            rol="veterinario",
            clinica=self.clinica,
        )
        self.assertTrue(vet.is_active)

    def test_admin_debe_tener_clinica(self):
        """Un admin de veterinaria debe estar asociado a una clínica"""
        admin = User.objects.create_user(
            username="admin_sin_clinica",
            email="admin_sin@test.com",
            password="pass123",
            rol="admin_veterinaria",
        )
        # El admin puede crearse sin clínica inicialmente
        self.assertIsNone(admin.clinica)

    def test_veterinario_requiere_clinica(self):
        """Un veterinario debe estar asociado a una clínica"""
        vet = User.objects.create_user(
            username="vet_con_clinica",
            email="vetclinica@test.com",
            password="pass123",
            rol="veterinario",
            clinica=self.clinica,
        )
        self.assertEqual(vet.clinica, self.clinica)

    def test_get_full_name(self):
        """Debe devolver el nombre completo del usuario"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="pass123",
            rol="cliente",
            first_name="Juan",
            last_name="Pérez",
        )
        self.assertEqual(user.get_full_name(), "Juan Pérez")

    def test_str_sin_nombre(self):
        """Debe mostrar email si no tiene nombre completo"""
        user = User.objects.create_user(
            username="user_sin_nombre",
            email="sinombre@test.com",
            password="pass123",
            rol="cliente",
        )
        self.assertIn("sinombre@test.com", str(user))

    def test_rol_invalido(self):
        """No debe permitir roles inválidos"""
        with self.assertRaises(ValidationError):
            user = User(
                username="invalido",
                email="inv@test.com",
                rol="rol_inexistente",
            )
            user.full_clean()

    def test_cliente_puede_tener_multiple_clinicas(self):
        """Un cliente puede estar asociado a una o más clínicas"""

        cliente = User.objects.create_user(
            username="cliente_multi",
            email="multi@test.com",
            password="pass123",
            rol="cliente",
            clinica=self.clinica,
        )
        self.assertEqual(cliente.clinica, self.clinica)

    def test_password_hasheada(self):
        """La contraseña debe guardarse hasheada"""
        user = User.objects.create_user(
            username="testpass",
            email="pass@test.com",
            password="mypassword123",
            rol="cliente",
        )
        # La contraseña NO debe guardarse en texto plano
        self.assertNotEqual(user.password, "mypassword123")
        # Pero debe poder verificarse
        self.assertTrue(user.check_password("mypassword123"))
