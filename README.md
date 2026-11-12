# CineFlix — Flask + PostgreSQL / SQLite

Aplicación web didáctica para registrar, consultar y cancelar reservaciones de cine. El diseño utiliza una interfaz oscura inspirada en plataformas de streaming, con acentos rojos.

## Funciones

- Formulario de reservación con nombre, correo, película, fecha, horario, boletos y sala.
- Validación de datos en el servidor.
- Persistencia en PostgreSQL (Render + Neon) o SQLite para desarrollo local.
- Consulta de reservaciones y búsqueda por cliente, correo o película.
- Cancelación de una reservación.
- Mensajes de confirmación y errores.
- Token CSRF sencillo para formularios POST.
- Ruta de salud: `/salud`.

## Requisitos

- Python 3.10 o superior.
- Visual Studio Code.
- Dependencias instaladas desde `requirements.txt`.

## Instalación en Windows

Abre esta carpeta en Visual Studio Code y abre Terminal → Nueva terminal.

### 1. Crear entorno virtual

```powershell
py -m venv .venv
```

### 2. Activar entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, puedes ejecutar los comandos con `.venv\Scripts\python.exe` directamente o usar la terminal CMD y ejecutar:

```bat
.venv\Scripts\activate.bat
```

### 3. Instalar dependencias

```bash
python -m pip install -r requirements.txt
```

### 4. Ejecutar

```bash
python app.py
```

Abre en el navegador:

- Formulario: http://127.0.0.1:5002/
- Reservaciones: http://127.0.0.1:5002/reservaciones
- Estado: http://127.0.0.1:5002/salud

Si no defines `DATABASE_URL`, la base local `cineflix.db` se crea automáticamente junto a `app.py`.

## Desplegar en Render con Neon

1. Sube el proyecto a un repositorio Git.
2. En [Neon](https://neon.tech/), crea un proyecto PostgreSQL. En **Connect**, copia la cadena de conexión pooled, que debe comenzar con `postgresql://` y usar `sslmode=require`.
3. En [Render](https://render.com/), crea un **Blueprint** y selecciona el repositorio. Render detectará `render.yaml` y configurará el servicio web.
4. Cuando Render solicite `DATABASE_URL`, pega la cadena de conexión de Neon. `SECRET_KEY` se genera de forma segura mediante el Blueprint.
5. Inicia el despliegue. Render instalará `requirements.txt`, ejecutará Gunicorn y comprobará `/salud`, que también verifica la conexión a la base de datos.

No publiques ni subas la cadena de Neon ni otros secretos al repositorio. La aplicación crea la tabla al iniciar si aún no existe; no migra automáticamente cambios posteriores de esquema. Los registros que tengas en el archivo local `cineflix.db` no se copian automáticamente a Neon.

## Estructura

```text
CineFlix/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── reserva.html
│   └── listado.html
└── static/
    ├── estilos.css
    └── app.js
```

## Pruebas manuales

1. Registra una reservación con todos los datos válidos.
2. Comprueba que aparezca el mensaje de éxito.
3. Entra a `/reservaciones` y verifica que aparezca el registro.
4. Busca por nombre, correo o película.
5. Intenta enviar un formulario con datos incorrectos.
6. Cancela una reservación y comprueba que desaparezca.
7. Detén el servidor y vuelve a iniciarlo; los registros deben permanecer.

## Conceptos importantes para explicar

- **Flask:** recibe las peticiones del navegador y decide qué función ejecutar.
- **GET:** solicita y muestra páginas o información.
- **POST:** envía datos del formulario para guardarlos o cancelar un registro.
- **request.form:** permite leer los datos enviados por el formulario.
- **SQLite:** base de datos que guarda la información por defecto en el archivo local `cineflix.db`; en Render se usa PostgreSQL mediante `DATABASE_URL`.
- **INSERT:** agrega una reservación.
- **SELECT:** consulta las reservaciones.
- **DELETE:** elimina una reservación.
- **commit():** confirma los cambios en la base de datos.
- **Jinja:** permite insertar datos de Python dentro de las plantillas HTML.

## Alcance y seguridad

Este proyecto no comprueba asientos disponibles, no procesa pagos ni emite boletos reales. El acceso a reservaciones y su cancelación no incluye autenticación; añade controles de acceso antes de usarlo con datos reales. El token CSRF incluido es una protección didáctica básica, no sustituye una auditoría de seguridad.
