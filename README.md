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

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

Te pedirá:
- **Email**: admin@veterinaria.com (o el que prefieras)
- **Nombre completo**: Administrador del Sistema
- **Password**: (elige una contraseña segura)
- **Confirmar password**: (repite la contraseña)

### 7. Cargar Datos de Prueba

```bash
python manage.py crear_datos_prueba
```

Este comando carga:
- 1 clínica veterinaria de ejemplo
- 1 administrador de veterinaria
- 1 veterinarios
- 1 cliente activo
- 1 cliente en estado pendiente

### 8. Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

Accede a la aplicación en: **http://127.0.0.1:8000/**

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


## Base de Datos (no implementado todavía)

Por defecto, el proyecto usa **SQLite** para desarrollo. Para usar PostgreSQL en producción:

1. Instala PostgreSQL
2. Crea una base de datos
3. Actualiza tu `.env`:

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/veterinaria_db
```

4. Instala el adaptador:
```bash
pip install psycopg2-binary
```

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

## Seguridad

⚠️ **IMPORTANTE para producción:**

1. Cambia `SECRET_KEY` en `.env`
2. Establece `DEBUG=False`
3. Configura `ALLOWED_HOSTS` correctamente
4. Usa HTTPS
5. Configura correctamente CORS y CSRF
6. Usa variables de entorno para datos sensibles

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

# [ACTUALIZACIÓN] - Gestión Mascotas 

Migrar Datos Modelo Mascota

```bash
python manage.py makemigrations mascotas
```
```bash
python manage.py migrate
```
Cargar especies y razas

```bash
python manage.py cargar_especies
```
 Instalar dependencia (carga de imagenes)

 ```bash
pip install pillow
```

## Capturas actuales

### Principal

<img width="1366" height="727" alt="principal" src="https://github.com/user-attachments/assets/d08788eb-1961-465e-b8cf-f01d61d83371" />

### Detalle Veterinaria

<img width="1366" height="731" alt="detalle_veterinaria" src="https://github.com/user-attachments/assets/5c11ddf9-6e9f-492a-b8d6-7cb957cf7a8d" />

### Opciones de Registro

<img width="1366" height="723" alt="opciones_registro" src="https://github.com/user-attachments/assets/71c765c3-87f5-4c57-ad70-0977963825d6" />

### Formulario de Pre Registro

<img width="1366" height="729" alt="pre_registro_cliente" src="https://github.com/user-attachments/assets/cf42eecb-7b54-48a7-b133-6770ffd59fbc" />
<img width="1366" height="727" alt="pre_registro_cliente_2" src="https://github.com/user-attachments/assets/4a1040b3-d361-4632-bb38-27cc89cb73df" />

### Dashboard Administrador

<img width="1366" height="725" alt="dashboard_admin" src="https://github.com/user-attachments/assets/d5ab34c6-613c-42a6-95cf-43308bd1dc53" />

### Dashboard Veterinario

<img width="1366" height="729" alt="dashboard_veterinario" src="https://github.com/user-attachments/assets/41f61ddd-3dcc-4665-a8e4-1cec6bc9a678" />

### Dashboard Cliente

<img width="1366" height="723" alt="dashboard_cliente" src="https://github.com/user-attachments/assets/be69a06e-1994-4217-b8f2-c182d4005f6c" />
<img width="1366" height="725" alt="dashborad_cliente" src="https://github.com/user-attachments/assets/0056373d-e3e6-45a4-a0f9-7b4bd8a7477d" />

## Documentación Adicional

- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/) (para el frontend)

##  Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
