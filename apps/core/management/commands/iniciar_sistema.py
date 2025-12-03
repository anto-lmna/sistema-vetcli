from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Ejecuta todos los scripts de carga de datos iniciales en orden"

    def handle(self, *args, **options):
        self.stdout.write("🚀 INICIANDO CARGA COMPLETA DEL SISTEMA...\n")

        # 1. Cargar Tablas de Referencia (Catalogos)
        # Es mejor cargar primero lo estático (Estados, Especies)
        self.stdout.write("--- Paso 1: Cargando Estados de Turnos ---")
        call_command('cargar_estados_turnos')
        
        self.stdout.write("\n--- Paso 2: Cargando Especies y Razas ---")
        call_command('cargar_especies')

        # 2. Cargar Datos Transaccionales / Maestros
        # Usuarios, Clínicas, etc.
        self.stdout.write("\n--- Paso 3: Creando Usuarios y Clínica ---")
        call_command('crear_datos_prueba')

        # Mensaje final
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("✅ SISTEMA INICIALIZADO CORRECTAMENTE"))
        self.stdout.write("="*50)