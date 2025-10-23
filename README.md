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
- **Email**: admin@veterinaria.com (puede quedar vacio)
- **Nombre completo**: admin
- **Password**: (ponen algo simple "admin123")
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

## [ACTUALIZACIÓN] - Gestión de Mascotas 

Migrar Datos del Modelo Mascota

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
 Instalar dependencia (procesamiento de imagenes)

 ```bash
pip install pillow
```

### Caracteristicas añadidas

#### **Clientes**

Los clientes pueden administrar sus propias mascotas desde su perfil.

**Funciones disponibles:**
* ➕ Agregar nuevas mascotas.
* ✏️ Editar datos de sus mascotas.
* 👁️ Ver detalle de cada mascota.
* 📋 Visualizar el listado completo de *“Mis Mascotas”*.

---

#### **Administrador**

El administrador tiene control total sobre las mascotas registradas en la veterinaria.

**Funciones disponibles:**
* 👁️ Ver todas las mascotas de la veterinaria.
* ✏️ Editar información de mascotas.
* 🔄 Activar o Inactivar mascotas según su estado.

---

#### **Veterinario**

El veterinario puede acceder a la información de los pacientes que atiende.

**Funciones disponibles:**
* 👁️ Ver listado de pacientes (mascotas).
* 📄 Consultar el detalle de cada paciente.

---

## [ACTUALIZACIÓN 2 ] - Gestión de Turnos 

Recomiendo eliminar el db.sqlite3 y realizar los siguientes pasos nuevamente:

```bash
python manage.py makemigrations 
```
```bash
python manage.py migrate
```
```bash
python manage.py crear_datos_prueba
```
```bash
python manage.py cargar_especies
```
```bash
python manage.py cargar_estados_turnos
```

_*Si solo quieren cargar el modelo Turnos_:

**Migrar Datos del Modelo Turno**

```bash
python manage.py makemigrations turnos
```
```bash
python manage.py migrate
```

```bash
python manage.py cargar_estados_turnos
```

### Caracteristicas añadidas:

#### **Cliente**

* 📅 Ver turnos disponibles
* 🔍 Buscar turnos por **veterinario** y **día**
* 📝 Solicitar turno
* ❌ Cancelar turno
* 👁️ Ver detalle del turno

---

#### **Veterinario**

* 🗓️ Ver su **agenda de turnos**
* ➕ Crear **disponibilidades** de atención
* 👁️ Ver detalle de turno
* 🗑️ Eliminar disponibilidad *(solo si no tiene turnos reservados)*

---

#### **Administrador**

* 🗓️ Ver agenda completa
* 🧾 Crear turnos **manualmente**
* ❌ Cancelar turnos

---




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

<img width="1366" height="688" alt="dashboard_admin" src="https://github.com/user-attachments/assets/8d778694-b4fa-4793-9d49-a4be85f5a6ba" />


### Dashboard Veterinario

<img width="1366" height="690" alt="dashboard_veterinario" src="https://github.com/user-attachments/assets/82189344-c8ec-4a29-9023-08d52a41ea27" />


### Dashboard Cliente
<img width="1366" height="692" alt="dashboard_cliente" src="https://github.com/user-attachments/assets/d82e8f6e-3d07-49e9-9947-dfb4a078219c" />

### Perfil Cliente
<img width="1366" height="692" alt="perfil_cliente" src="https://github.com/user-attachments/assets/80d614e9-7229-4b2e-92b4-5a7ebef6f59f" />

### Gestión Mascotas

#### Agregar mascota
<img width="1366" height="657" alt="agregar_mascota)" src="https://github.com/user-attachments/assets/f536604b-4f15-4072-ac40-2c0351740246" />

#### Detalle Mascota
<img width="1366" height="677" alt="detalle_mascota" src="https://github.com/user-attachments/assets/8f80d234-dd61-4478-80d9-c33c504bdc5c" />

#### Mascotas Registradas
<img width="1366" height="680" alt="mascotas_registradas_admin_2" src="https://github.com/user-attachments/assets/f0234166-4cf2-484b-aa02-fbfc00c4dcc2" />

#### Inactivar Mascota
<img width="1366" height="688" alt="inactivar_mascota" src="https://github.com/user-attachments/assets/a0e8d3de-68bc-411e-92fc-a466b505ac8a" />

### Gestión Turnos

#### Agenda administrador

<img width="1366" height="685" alt="agenda_clinica_admin" src="https://github.com/user-attachments/assets/799355e4-f31e-454d-b32d-b8506f5cfaab" />

#### Agenda Veterinario

<img width="1366" height="700" alt="agenda_veterinario" src="https://github.com/user-attachments/assets/d41a75c1-f243-4b2d-8543-54612796ce1f" />

#### Crear disponibilidad

<img width="1366" height="686" alt="publicar_disponibilidad" src="https://github.com/user-attachments/assets/8935055e-bcbf-4fc5-ba4b-5941a4690cf7" />

<img width="1366" height="437" alt="disponibilidades" src="https://github.com/user-attachments/assets/e0a36610-7e84-4450-a270-539612a63fc5" />

#### Crear Turno Manual

<img width="1366" height="688" alt="turno_manual_admin" src="https://github.com/user-attachments/assets/fd921879-ef30-4d08-a3a7-fde9baa125d8" />

#### Crear/Eliminar/Ver turnos (cliente)

<img width="1366" height="688" alt="turnos_disponibles" src="https://github.com/user-attachments/assets/b487c3d5-6214-4a52-a905-42609e1f4016" />

<img width="1366" height="684" alt="reservar_turno" src="https://github.com/user-attachments/assets/89b96f16-3417-490b-a256-61e96b00c561" />

<img width="1366" height="686" alt="mis_turnos" src="https://github.com/user-attachments/assets/3d506390-7298-4047-83c2-d6b178cefb6e" />

<img width="1366" height="671" alt="detalle_turno" src="https://github.com/user-attachments/assets/6f707be8-3a6f-443e-ac53-ef4fc37384e4" />

<img width="1366" height="680" alt="cancelar_turno" src="https://github.com/user-attachments/assets/0a83834b-ed03-4a95-b75a-34d1b783c6a1" />










## Documentación Adicional

- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/) (para el frontend)

##  Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
