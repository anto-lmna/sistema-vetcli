# Sistema VetCli para Veterinarias

Sistema de gestión integral para clínicas veterinarias desarrollado en Django, que permite administrar turnos, historiales médicos, pacientes y personal.

## Características Principales

### Roles de Usuario

**Administrador de Veterinaria**
- Gestión completa de la clínica
- Alta de veterinarios
- Activación de clientes pre-registrados
- Publicación de calendarios y turnos
- Gestión de mascotas (inactivar/activar)

**Veterinario**
- Visualización de clientes y mascotas
- Gestión de turnos
- Creación y edición de historiales clínicos
- Emisión de recetas
- Visualización de agenda

**Cliente (Dueño de Mascotas)**
- Pre-registro (requiere activación del admin)
- Solicitud de turnos
- Gestión de datos de mascotas
- Visualización de historiales clínicos
- Descarga de recetas y documentos


### Estructura del Proyecto

```
veterinaria_saas/
├── config/                 # Configuración principal del proyecto
├── apps/
│   ├── accounts/          # Gestión de usuarios y autenticación
│   ├── clinicas/          # Gestión de veterinarias/clínicas
│   ├── mascotas/          # Gestión de mascotas/pacientes
│   ├── turnos/            # Sistema de turnos y citas
│   ├── historiales/       # Historiales médicos
│   └── core/              # Funcionalidades compartidas
├── templates/             # Plantillas HTML
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── media/                 # Archivos subidos por usuarios
├── requirements.txt       # Dependencias del proyecto
└── manage.py             # Script de gestión de Django
```

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/anto-lmna/sistema-vetcli.git
cd sistema-vetcli
```

### 2. Crear y Activar Entorno Virtual

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 **Nota**: Verás `(venv)` al inicio de tu línea de comandos cuando el entorno esté activado.

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Aplicar Migraciones
Solo deben aplicarse cuando se realizan cambios en el Modelo. En este caso solo se necesita ejecutarlo la primera vez.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

Te pedirá:
- **Email**: admin@veterinaria.com (puede quedar vacio)
- **Nombre completo**: admin
- **Password**: (ponen algo simple "admin123")
- **Confirmar password**: (repite la contraseña)

### 7. Cargar Datos Iniciales

```bash
python manage.py iniciar_sistema
```
Este comando carga:
- 1 clínica veterinaria de ejemplo
- 1 administrador de veterinaria
- 1 veterinarios
- 1 cliente activo
- 1 cliente en estado pendiente
- Estados de Turno
- Razas mascotas

### 8. Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

##  Usuarios de Prueba

Después de cargar los datos de prueba, se pueden usar estas credenciales:

### Administrador de Veterinaria
   - **Username**: admin_vet
   - **Email**: admin@veterinaria.com
   - **Password**: admin123
  
### Veterinario
   - **Username**: dr_lopez
   - **Email**: lopez@veterinaria.com
   - **Password**: vet123

### Cliente Activo
   - **Username**: cliente_activo
   - **Email**: cliente@gmail.com
   - **Password**: cliente123

#### Cliente Pendiente
   - **Username**: cliente_pendiente
   - **Email**: pendiente@gmail.com
   - **Password**: pendiente123

## Ejecución de Unit Test
### Gestión turnos
```bash
python manage.py test apps.turnos
```
### Accounts

```bash
python manage.py test apps.accounts
```
### General
```bash
python manage.py test
```

Revisá la salida en la terminal:

- . → test pasó
- F → test falló
- E → error durante el test

## Archivos Importantes

### `requirements.txt`
Contiene todas las dependencias del proyecto:

```
Django==4.2.7
Pillow==10.1.0
django-crispy-forms==2.1
crispy-bootstrap5==2.0.0
python-decouple==3.8
django-extensions==3.2.3
```

## Solución de Problemas

#### Error: "No module named 'apps'"
```bash
# Verifica que estés en el directorio correcto
cd sistema-vetcli
# Asegúrate de que el entorno virtual esté activado
```

#### Error: "Table doesn't exist"
```bash
# Ejecuta las migraciones
python manage.py migrate
```

#### Error al cargar fixtures
```bash
# Elimina la base de datos y vuelve a crear
rm db.sqlite3
python manage.py migrate
python manage.py crear_datos_prueba
```

#### Puerto 8000 ocupado
```bash
# Usa otro puerto
python manage.py runserver 8080
```

## Capturas actuales

### Dashboard Administrador

<img width="1112" height="595" alt="image" src="https://github.com/user-attachments/assets/1ac7c12b-a826-4f2e-8938-7abacfaac434" />

### Dashboard Veterinario

<img width="1109" height="594" alt="image" src="https://github.com/user-attachments/assets/14bc9d7a-06cf-4bac-9d54-a06da0b9bd42" />

### Dashboard Cliente
<img width="1106" height="565" alt="image" src="https://github.com/user-attachments/assets/ccd73d40-e87f-4616-90c7-ade9a69b1ffe" />
<img width="1110" height="561" alt="image" src="https://github.com/user-attachments/assets/ce6e47e6-66cf-4346-a8d1-661494d53f65" />

### Perfil Cliente
<img width="1113" height="591" alt="image" src="https://github.com/user-attachments/assets/2055e78b-225a-4b2d-8c8c-d22ed778cb81" />

### Gestión Mascotas

#### Agregar mascota
<img width="1366" height="657" alt="agregar_mascota)" src="https://github.com/user-attachments/assets/f536604b-4f15-4072-ac40-2c0351740246" />

#### Detalle Mascota
<img width="1366" height="677" alt="detalle_mascota" src="https://github.com/user-attachments/assets/8f80d234-dd61-4478-80d9-c33c504bdc5c" />

#### Mascotas Registradas
<img width="1104" height="594" alt="image" src="https://github.com/user-attachments/assets/fc3c7012-d5f9-4abe-9258-1320e80d7158" />

### Gestión Turnos

#### Agenda administrador
<img width="1106" height="592" alt="image" src="https://github.com/user-attachments/assets/75c9f06d-e21b-48a4-876f-f2005d57d6a4" />


#### Agenda Veterinario
<img width="1108" height="597" alt="image" src="https://github.com/user-attachments/assets/f0bdaa62-4480-482c-9af6-72ff0720637e" />

#### Crear disponibilidad

<img width="1366" height="686" alt="publicar_disponibilidad" src="https://github.com/user-attachments/assets/8935055e-bcbf-4fc5-ba4b-5941a4690cf7" />

<img width="1366" height="437" alt="disponibilidades" src="https://github.com/user-attachments/assets/e0a36610-7e84-4450-a270-539612a63fc5" />

#### Crear Turno Manual

<img width="1366" height="688" alt="turno_manual_admin" src="https://github.com/user-attachments/assets/fd921879-ef30-4d08-a3a7-fde9baa125d8" />

#### Crear Consulta

<img width="1103" height="595" alt="image" src="https://github.com/user-attachments/assets/6399b4fb-609d-4f8e-b214-dc1d96fa5916" />
<img width="1106" height="534" alt="image" src="https://github.com/user-attachments/assets/3413ce3e-18e0-4ab9-a46c-6eed1fef1cf6" />

#### Lista Consultas
<img width="1119" height="592" alt="image" src="https://github.com/user-attachments/assets/4b626f82-ccd7-4775-8f4b-8b8c2e1ce497" />

## Documentación Adicional

- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/) (para el frontend)

##  Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
