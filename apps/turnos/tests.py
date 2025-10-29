from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, time, date
from django.core.exceptions import ValidationError

from apps.clinicas.models import Clinica
from apps.accounts.models import CustomUser
from apps.turnos.forms import TurnoCrearAdminForm
from apps.mascotas.models import Mascota, Especie, Raza
from apps.turnos.models import Turno, EstadoTurno, DisponibilidadVeterinario


# ==================== TESTS DE MODELOS ====================


class EstadoTurnoModelTest(TestCase):
    """Tests para el modelo EstadoTurno"""

    def test_crear_estados_basicos(self):
        """Test: Crear estados básicos del sistema"""
        pendiente = EstadoTurno.objects.create(
            nombre="Pendiente", codigo=EstadoTurno.PENDIENTE, color="#ffc107"
        )
        confirmado = EstadoTurno.objects.create(
            nombre="Confirmado", codigo=EstadoTurno.CONFIRMADO, color="#28a745"
        )

        self.assertEqual(pendiente.codigo, "pendiente")
        self.assertEqual(confirmado.codigo, "confirmado")
        self.assertTrue(pendiente.activo)

    def test_estado_codigo_unico(self):
        """Test: No permite códigos duplicados"""
        EstadoTurno.objects.create(nombre="Estado 1", codigo=EstadoTurno.PENDIENTE)

        with self.assertRaises(Exception):
            EstadoTurno.objects.create(
                nombre="Estado 2", codigo=EstadoTurno.PENDIENTE  # Duplicado
            )


class TurnoModelTest(TestCase):
    """Tests para el modelo Turno"""

    def setUp(self):
        """Configuración inicial para todos los tests"""
        # Crear admin primero
        self.admin = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="test",
            first_name="Admin",
            last_name="Test",
            rol="admin_veterinaria",
        )

        # Crear clínica con admin
        self.clinica = Clinica.objects.create(
            nombre="Veterinaria Test",
            email="test@vet.com",
            hora_apertura=time(9, 0),
            hora_cierre=time(18, 0),
            admin=self.admin,
        )

        # Asignar clínica al admin
        self.admin.clinica = self.clinica
        self.admin.save()

        # Crear veterinario
        self.veterinario = CustomUser.objects.create_user(
            username="vet_test",
            email="vet@test.com",
            password="testpass123",
            first_name="Carlos",
            last_name="Veterinario",
            rol="veterinario",
            clinica=self.clinica,
        )

        # Crear cliente
        self.cliente = CustomUser.objects.create_user(
            username="cli_test",
            email="cliente@test.com",
            password="testpass123",
            first_name="Juan",
            last_name="Cliente",
            rol="cliente",
        )
        self.cliente.is_active = True
        self.cliente.pendiente_aprobacion = False
        self.cliente.clinica = self.clinica
        self.cliente.save()

        # Crear especie y raza
        self.especie = Especie.objects.create(nombre="Perro")
        self.raza = Raza.objects.create(nombre="Labrador", especie=self.especie)

        # Crear mascota
        self.mascota = Mascota.objects.create(
            nombre="Firulais",
            especie=self.especie,
            raza=self.raza,
            dueno=self.cliente,
            fecha_nacimiento=date(2020, 1, 1),
            sexo="macho",
        )

        # Crear estados
        self.estado_pendiente = EstadoTurno.objects.create(
            nombre="Pendiente", codigo=EstadoTurno.PENDIENTE
        )
        self.estado_confirmado = EstadoTurno.objects.create(
            nombre="Confirmado", codigo=EstadoTurno.CONFIRMADO
        )
        self.estado_completado = EstadoTurno.objects.create(
            nombre="Completado", codigo=EstadoTurno.COMPLETADO
        )

    def test_crear_turno_disponible(self):
        """Test: Crear turno disponible (sin cliente)"""
        fecha = timezone.now().date() + timedelta(days=1)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        self.assertIsNotNone(turno.id)
        self.assertFalse(turno.reservado)
        self.assertIsNone(turno.cliente)
        self.assertIsNone(turno.mascota)
        self.assertEqual(turno.hora_fin, time(10, 30))

    def test_turno_calcula_hora_fin_automaticamente(self):
        """Test: hora_fin se calcula automáticamente"""
        fecha = timezone.now().date() + timedelta(days=1)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(14, 0),
            duracion_minutos=45,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        self.assertEqual(turno.hora_fin, time(14, 45))

    def test_reservar_turno_exitoso(self):
        """Test: Reservar un turno disponible"""
        fecha = timezone.now().date() + timedelta(days=2)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(11, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        # Reservar
        turno.reservar(self.cliente, self.mascota)

        self.assertTrue(turno.reservado)
        self.assertEqual(turno.cliente, self.cliente)
        self.assertEqual(turno.mascota, self.mascota)
        self.assertEqual(turno.estado.codigo, EstadoTurno.CONFIRMADO)

    def test_no_permite_reservar_turno_ya_reservado(self):
        """Test: No permite reservar un turno ya reservado"""
        fecha = timezone.now().date() + timedelta(days=2)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(11, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        turno.reservar(self.cliente, self.mascota)

        # Crear otro cliente
        otro_cliente = CustomUser.objects.create_user(
            username="otro_cli",
            email="otro@test.com",
            password="test",
            first_name="Otro",
            last_name="Cliente",
            rol="cliente",
        )

        otra_mascota = Mascota.objects.create(
            nombre="Rex",
            especie=self.especie,
            dueno=otro_cliente,
            fecha_nacimiento=date(2019, 1, 1),
            sexo="macho",
        )

        # Intentar reservar nuevamente
        with self.assertRaises(ValueError) as context:
            turno.reservar(otro_cliente, otra_mascota)

        self.assertIn("ya está reservado", str(context.exception))

    def test_no_permite_reservar_mascota_de_otro_cliente(self):
        """Test: No permite reservar con mascota que no pertenece al cliente"""
        fecha = timezone.now().date() + timedelta(days=2)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(11, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        # Crear otro cliente
        otro_cliente = CustomUser.objects.create_user(
            username="otro_cli",
            email="otro@test.com",
            password="test",
            first_name="Otro",
            last_name="Cliente",
            rol="cliente",
        )

        # Intentar reservar con mascota de otro cliente
        with self.assertRaises(ValueError) as context:
            turno.reservar(otro_cliente, self.mascota)

        self.assertIn("no pertenece al cliente", str(context.exception))

    def test_no_permite_reservar_turno_pasado(self):
        """Test: No permite reservar turnos en el pasado"""
        fecha_pasada = timezone.now().date() - timedelta(days=1)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha_pasada,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        with self.assertRaises(ValueError) as context:
            turno.reservar(self.cliente, self.mascota)

        self.assertIn("pasado", str(context.exception))

    def test_unique_together_veterinario_fecha_hora(self):
        """Test: No permite duplicar veterinario + fecha + hora"""
        fecha = timezone.now().date() + timedelta(days=1)

        Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        with self.assertRaises(Exception):
            Turno.objects.create(
                clinica=self.clinica,
                veterinario=self.veterinario,
                fecha=fecha,
                hora_inicio=time(10, 0),
                duracion_minutos=30,
                estado=self.estado_pendiente,
                creado_por=self.veterinario,
            )


class DisponibilidadVeterinarioTest(TestCase):
    """Tests para DisponibilidadVeterinario"""

    def setUp(self):
        # Crear admin
        self.admin = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="test",
            first_name="Admin",
            last_name="Test",
            rol="admin_veterinaria",
        )

        # Crear clínica con admin
        self.clinica = Clinica.objects.create(
            nombre="Veterinaria Test",
            email="test@vet.com",
            hora_apertura=time(9, 0),
            hora_cierre=time(18, 0),
            admin=self.admin,
        )

        self.admin.clinica = self.clinica
        self.admin.save()

        self.veterinario = CustomUser.objects.create_user(
            username="vet_test",
            email="vet@test.com",
            password="test",
            first_name="Carlos",
            last_name="Vet",
            rol="veterinario",
            clinica=self.clinica,
        )

        self.estado_pendiente = EstadoTurno.objects.create(
            nombre="Pendiente", codigo=EstadoTurno.PENDIENTE
        )

    def test_crear_disponibilidad(self):
        """Test: Crear bloque de disponibilidad"""
        disp = DisponibilidadVeterinario.objects.create(
            veterinario=self.veterinario,
            clinica=self.clinica,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=7),
            hora_inicio=time(9, 0),
            hora_fin=time(13, 0),
            duracion_turno=30,
        )

        self.assertIsNotNone(disp.id)
        self.assertEqual(disp.duracion_turno, 30)

    def test_validacion_hora_inicio_menor_hora_fin(self):
        """Test: Validar que hora_inicio < hora_fin"""
        disp = DisponibilidadVeterinario(
            veterinario=self.veterinario,
            clinica=self.clinica,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=7),
            hora_inicio=time(14, 0),
            hora_fin=time(10, 0),
            duracion_turno=30,
        )

        with self.assertRaises(ValidationError):
            disp.clean()

    def test_validacion_fecha_inicio_menor_fecha_fin(self):
        """Test: Validar que fecha_inicio <= fecha_fin"""
        disp = DisponibilidadVeterinario(
            veterinario=self.veterinario,
            clinica=self.clinica,
            fecha_inicio=date.today() + timedelta(days=7),
            fecha_fin=date.today(),
            hora_inicio=time(9, 0),
            hora_fin=time(13, 0),
            duracion_turno=30,
        )

        with self.assertRaises(ValidationError):
            disp.clean()

    def test_generar_turnos_rango(self):
        """Test: Generar turnos automáticamente"""
        disp = DisponibilidadVeterinario.objects.create(
            veterinario=self.veterinario,
            clinica=self.clinica,
            fecha_inicio=date.today() + timedelta(days=1),
            fecha_fin=date.today() + timedelta(days=1),  # Solo un día
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),  # 2 horas
            duracion_turno=30,  # 4 turnos
        )

        turnos_creados = disp.generar_turnos_rango()

        self.assertEqual(turnos_creados, 4)
        self.assertEqual(Turno.objects.filter(veterinario=self.veterinario).count(), 4)

    def test_generar_turnos_no_duplica(self):
        """Test: No genera turnos que ya existen"""
        fecha = date.today() + timedelta(days=1)

        # Crear turno manual
        Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        # Crear disponibilidad que incluye ese horario
        disp = DisponibilidadVeterinario.objects.create(
            veterinario=self.veterinario,
            clinica=self.clinica,
            fecha_inicio=fecha,
            fecha_fin=fecha,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            duracion_turno=30,
        )

        turnos_creados = disp.generar_turnos_rango()

        # Solo debe crear 1 turno (10:30), el de 10:00 ya existe
        self.assertEqual(turnos_creados, 1)
        self.assertEqual(Turno.objects.filter(veterinario=self.veterinario).count(), 2)


# # ==================== TESTS DE FORMULARIOS ====================


class TurnoCrearAdminFormTest(TestCase):
    """Tests para el formulario de crear turno (admin)"""

    def setUp(self):
        # Crear admin
        self.admin = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="test",
            first_name="Admin",
            last_name="Test",
            rol="admin_veterinaria",
        )

        # Crear clínica con admin
        self.clinica = Clinica.objects.create(
            nombre="Veterinaria Test",
            email="test@vet.com",
            hora_apertura=time(9, 0),
            hora_cierre=time(18, 0),
            admin=self.admin,
        )

        self.admin.clinica = self.clinica
        self.admin.save()

        self.veterinario = CustomUser.objects.create_user(
            username="vet_test",
            email="vet@test.com",
            password="test",
            first_name="Vet",
            last_name="Test",
            rol="veterinario",
            clinica=self.clinica,
        )

        self.cliente = CustomUser.objects.create_user(
            username="cli_test",
            email="cliente@test.com",
            password="test",
            first_name="Cliente",
            last_name="Test",
            rol="cliente",
            clinica=self.clinica,
        )

        self.especie = Especie.objects.create(nombre="Perro")
        self.mascota = Mascota.objects.create(
            nombre="Firulais",
            especie=self.especie,
            dueno=self.cliente,
            fecha_nacimiento=date(2020, 1, 1),
            sexo="macho",
        )

    def test_formulario_solo_muestra_veterinarios_de_clinica(self):
        """Test: Solo muestra veterinarios activos de la clínica"""
        # Crear admin para otra clínica
        otro_admin = CustomUser.objects.create_user(
            username="otro_admin",
            email="otro_admin@test.com",
            password="test",
            first_name="Otro",
            last_name="Admin",
            rol="admin_veterinaria",
        )

        # Crear otra clínica
        otra_clinica = Clinica.objects.create(
            nombre="Otra Clínica",
            email="otra@vet.com",
            hora_apertura=time(9, 0),
            hora_cierre=time(18, 0),
            admin=otro_admin,
        )

        otro_vet = CustomUser.objects.create_user(
            username="otra_vet",
            email="otro_vet@test.com",
            password="test",
            first_name="Otro",
            last_name="Vet",
            rol="veterinario",
            clinica=otra_clinica,
        )

        form = TurnoCrearAdminForm(user=self.admin)
        veterinarios = form.fields["veterinario"].queryset

        self.assertIn(self.veterinario, veterinarios)
        self.assertNotIn(otro_vet, veterinarios)


# # ==================== TESTS DE VISTAS ====================


class TurnoReservarViewTest(TestCase):
    """Tests para reservar turnos (cliente)"""

    def setUp(self):
        self.client_http = Client()

        # Crear admin
        self.admin = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="test",
            first_name="Admin",
            last_name="Test",
            rol="admin_veterinaria",
        )

        # Crear clínica con admin
        self.clinica = Clinica.objects.create(
            nombre="Veterinaria Test",
            email="test@vet.com",
            hora_apertura=time(9, 0),
            hora_cierre=time(18, 0),
            admin=self.admin,
        )

        self.admin.clinica = self.clinica
        self.admin.save()

        self.veterinario = CustomUser.objects.create_user(
            username="vet_test",
            email="vet@test.com",
            password="testpass123",
            first_name="Carlos",
            last_name="Vet",
            rol="veterinario",
            clinica=self.clinica,
        )

        self.cliente = CustomUser.objects.create_user(
            username="cli_test",
            email="cliente@test.com",
            password="testpass123",
            first_name="Juan",
            last_name="Cliente",
            rol="cliente",
            clinica=self.clinica,
        )
        self.cliente.is_active = True
        self.cliente.save()

        self.especie = Especie.objects.create(nombre="Perro")
        self.mascota = Mascota.objects.create(
            nombre="Firulais",
            especie=self.especie,
            dueno=self.cliente,
            fecha_nacimiento=date(2020, 1, 1),
            sexo="macho",
        )

        self.estado_pendiente = EstadoTurno.objects.create(
            nombre="Pendiente", codigo=EstadoTurno.PENDIENTE
        )

        self.estado_confirmado = EstadoTurno.objects.create(
            nombre="Confirmado", codigo=EstadoTurno.CONFIRMADO
        )

    def test_cliente_puede_reservar_turno_disponible(self):
        """Test: Cliente puede reservar un turno disponible"""
        fecha = timezone.now().date() + timedelta(days=2)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        self.client_http.login(username="cli_test", password="testpass123")

        response = self.client_http.post(
            reverse("turnos:reservar_turno", args=[turno.id]),
            {"mascota": self.mascota.id, "motivo": "Consulta general"},
        )

        turno.refresh_from_db()

        self.assertTrue(turno.reservado)
        self.assertEqual(turno.cliente, self.cliente)
        self.assertEqual(turno.mascota, self.mascota)
        self.assertEqual(turno.estado.codigo, EstadoTurno.CONFIRMADO)

    def test_dos_clientes_no_pueden_reservar_mismo_turno(self):
        """Test: No permite reservas concurrentes del mismo turno"""
        fecha = timezone.now().date() + timedelta(days=2)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            fecha=fecha,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_pendiente,
            creado_por=self.veterinario,
        )

        # Primer cliente reserva
        self.client_http.login(username="cli_test", password="testpass123")
        self.client_http.post(
            reverse("turnos:reservar_turno", args=[turno.id]),
            {"mascota": self.mascota.id},
        )

        # Crear segundo cliente
        otro_cliente = CustomUser.objects.create_user(
            username="otro_cliente",  # ← Este es el username correcto
            email="otro@test.com",
            password="testpass123",
            first_name="Otro",
            last_name="Cliente",
            rol="cliente",
            clinica=self.clinica,
        )
        otro_cliente.is_active = True
        otro_cliente.save()

        otra_mascota = Mascota.objects.create(
            nombre="Rex",
            especie=self.especie,
            dueno=otro_cliente,
            fecha_nacimiento=date(2019, 1, 1),
            sexo="macho",
        )

        # Segundo cliente intenta reservar el mismo turno
        self.client_http.logout()
        self.client_http.login(
            username="otro_cliente", password="testpass123"
        )  # ← Corregido

        response = self.client_http.post(
            reverse("turnos:reservar_turno", args=[turno.id]),
            {"mascota": otra_mascota.id},
        )

        # Verificar que el turno sigue siendo del primer cliente
        turno.refresh_from_db()
        self.assertEqual(turno.cliente, self.cliente)
        self.assertEqual(turno.mascota, self.mascota)


class TurnoCancelarClienteViewTest(TestCase):
    """Tests para cancelar turnos (cliente)"""

    def setUp(self):
        self.client_http = Client()

        # Crear admin
        self.admin = CustomUser.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="test",
            first_name="Admin",
            last_name="Test",
            rol="admin_veterinaria",
        )

        # Crear clínica con admin
        self.clinica = Clinica.objects.create(
            nombre="Veterinaria Test",
            email="test@vet.com",
            hora_apertura=time(9, 0),
            hora_cierre=time(18, 0),
            admin=self.admin,
        )

        self.admin.clinica = self.clinica
        self.admin.save()

        self.veterinario = CustomUser.objects.create_user(
            username="vet_test",
            email="vet@test.com",
            password="test",
            first_name="Vet",
            last_name="Test",
            rol="veterinario",
            clinica=self.clinica,
        )

        self.cliente = CustomUser.objects.create_user(
            username="cli_test",  # ← AGREGADO
            email="cliente@test.com",
            password="testpass123",
            first_name="Cliente",
            last_name="Test",
            rol="cliente",
            clinica=self.clinica,
        )
        self.cliente.is_active = True
        self.cliente.pendiente_aprobacion = False  # ← AGREGADO también
        self.cliente.save()

        self.especie = Especie.objects.create(nombre="Perro")
        self.mascota = Mascota.objects.create(
            nombre="Firulais",
            especie=self.especie,
            dueno=self.cliente,
            fecha_nacimiento=date(2020, 1, 1),
            sexo="macho",
        )

        self.estado_confirmado = EstadoTurno.objects.create(
            nombre="Confirmado", codigo=EstadoTurno.CONFIRMADO
        )

        self.estado_pendiente = EstadoTurno.objects.create(
            nombre="Pendiente", codigo=EstadoTurno.PENDIENTE
        )

        self.estado_completado = EstadoTurno.objects.create(
            nombre="Completado", codigo=EstadoTurno.COMPLETADO
        )

    def test_cliente_puede_cancelar_turno_con_anticipacion(self):
        """Test: Cliente puede cancelar con más de 2 horas de anticipación"""
        # Turno en 3 días
        fecha = timezone.now().date() + timedelta(days=3)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            cliente=self.cliente,
            mascota=self.mascota,
            fecha=fecha,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_confirmado,
            reservado=True,
            creado_por=self.veterinario,
        )

        self.client_http.login(
            username="cli_test", password="testpass123"
        )  # ← CORREGIDO

        response = self.client_http.post(
            reverse("turnos:cancelar_turno_cliente", args=[turno.id])
        )

        turno.refresh_from_db()

        self.assertFalse(turno.reservado)
        self.assertIsNone(turno.cliente)
        self.assertIsNone(turno.mascota)
        self.assertEqual(turno.estado.codigo, EstadoTurno.PENDIENTE)

    def test_cliente_no_puede_cancelar_turno_sin_anticipacion(self):
        """Test: No puede cancelar con menos de 2 horas"""
        # Turno en 1 hora (muy próximo)
        ahora = timezone.now()
        fecha = ahora.date()
        hora = (ahora + timedelta(hours=1)).time()

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            cliente=self.cliente,
            mascota=self.mascota,
            fecha=fecha,
            hora_inicio=hora,
            duracion_minutos=30,
            estado=self.estado_confirmado,
            reservado=True,
            creado_por=self.veterinario,
        )

        self.client_http.login(
            username="cli_test", password="testpass123"
        )  # ← CORREGIDO

        response = self.client_http.post(
            reverse("turnos:cancelar_turno_cliente", args=[turno.id])
        )

        turno.refresh_from_db()

        # El turno NO debe cancelarse
        self.assertTrue(turno.reservado)
        self.assertEqual(turno.cliente, self.cliente)

    def test_cliente_no_puede_cancelar_turno_completado(self):
        """Test: No puede cancelar un turno completado"""
        fecha = timezone.now().date() + timedelta(days=3)

        turno = Turno.objects.create(
            clinica=self.clinica,
            veterinario=self.veterinario,
            cliente=self.cliente,
            mascota=self.mascota,
            fecha=fecha,
            hora_inicio=time(10, 0),
            duracion_minutos=30,
            estado=self.estado_completado,
            reservado=True,
            creado_por=self.veterinario,
        )

        self.client_http.login(
            username="cli_test", password="testpass123"
        )  # ← CORREGIDO

        response = self.client_http.post(
            reverse("turnos:cancelar_turno_cliente", args=[turno.id])
        )

        turno.refresh_from_db()

        # El turno NO debe cancelarse
        self.assertTrue(turno.reservado)
        self.assertEqual(turno.estado.codigo, EstadoTurno.COMPLETADO)
