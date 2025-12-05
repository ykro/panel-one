# Prompt: Backend Development & Deployment - Panel One

## 1\. Objetivo

Migrar y escalar la lógica del script de prototipado existente (ubicado en el directorio `script/`) hacia una aplicación backend robusta y asíncrona dentro del directorio `backend/`. Todo el código generado debe compilar sin errores desde la primera ejecución.

**Importante:** Trabajarás en el mismo repositorio donde ya existe `script/`. No inicialices un nuevo repositorio git; crea el directorio `backend/` como hermano de `script/` y agrega allí todo el código nuevo.

El sistema debe mantener la lógica core de IA pero orquestarla mediante una API HTTP (FastAPI) con gestión de colas (Arq) y almacenamiento en nube (Google Cloud Storage) para permitir una arquitectura sin estado (Stateless) compatible con Google Cloud Run.

El entregable debe incluir la configuración necesaria para desplegar la solución como servicios de Cloud Run (API pública y Worker privado) y scripts de automatización.

IMPORTANTE: todo el código se ejecutará desde el directorio `backend/`, cuida los imports.

## 2\. Contexto Técnico

  * **Stack:** `uv` (Python 3.11+), FastAPI, Arq, Google GenAI SDK (v1.0+), GCS, Pillow, python-multipart.
  * **Logging:** `structlog` o `logging` estándar configurado para emitir JSON (Requisito indispensable para Cloud Run).
  * **Modelos (Constantes Inmutables):**
      * Texto: `gemini-3-pro-preview`
      * Imagen: `gemini-3-pro-image-preview`
      * **Restricción:** No implementar lógica de fallback. Si estos modelos fallan, lanzar excepción crítica.
  * **Infraestructura de Despliegue (Target):**
      * **API:** Cloud Run Service (Público).
      * **Worker:** Cloud Run Service (Privado, ejecución continua).
      * **Cola:** Redis (Upstash, soporte TLS).
      * **Almacenamiento:** Google Cloud Storage (Bucket `panel-one-outputs`).

## 3\. Estructura de Archivos y Fuentes

Es vital que **reutilices** el contenido probado del prototipo anterior y mantengas la estructura limpia.

```text
backend/
├── .gcp/                   # Crear directorio (JSON Service Account)
├── .env.example            # Plantilla de variables (ver 5.A)
├── .gitignore              # VITAL: Exclusiones de seguridad
├── .dockerignore           # Exclusiones Docker (client.py, .env, .gcp/, .git, .venv)
├── pyproject.toml          # Definición de dependencias y SCRIPTS
├── config.py               # Configuración centralizada (Pydantic)
├── schemas.py              # Modelos de datos y Enums
├── server.py               # API REST + WebSockets
├── worker.py               # Lógica de negocio Arq
├── run_worker.py           # Entrypoint de Python para el Worker
├── storage.py              # Lógica GCS
├── utils.py                # Wrapper Gemini y Logging config
├── setup_gcs.py            # Setup inicial del bucket
├── client.py               # CLI App (Basado en lógica de script/main.py)
├── story_prompt.md         # COPIAR de script/story_prompt.md
├── imagegen_prompt.md      # COPIAR de script/imagegen_prompt.md
├── Dockerfile              # Imagen para API Service
├── Dockerfile.worker       # Imagen para Worker Service
├── run_worker.sh           # Script de entrada (Bash) para Worker Service en Cloud Run
└── deploy.sh               # Script de automatización de deploy
```

## 4\. Restricciones de Implementación

1.  **SDK Google GenAI v1.0:** Importar siempre `from google import genai` y usar `client.models.generate_content`.
2.  **Manejo de Archivos (GCS vs Local):**
      * **API:** Recibe imágenes, las sube a GCS (`inputs/{job_id}/...`) y pasa las **URLs de GCS** (`list[str]`) al trabajo de Arq.
      * **Worker:** Recibe URLs de GCS, descarga los archivos a `/tmp` localmente con un **timeout estricto (e.g., 60s)**, procesa y sube resultados finales. Elimina archivos de input de GCS tras completar o fallar.
3.  **Serialización en Arq:** Pasar únicamente listas de strings (URLs), nunca objetos PIL o bytes.
4.  **Arq Usage:** Para consultar el estado de un trabajo, NO uses `redis_pool.job(job_id)`. Debes importar Job desde arq.jobs e instanciarlo explícitamente: `Job(job_id, redis_pool)`.
5.  **Ejecución Asíncrona:** Envolver llamadas IO (GCS/GenAI) en `asyncio.to_thread`.
6.  **Entorno y Rutas:** Asumir ejecución desde `backend/`. (no usar prefijo backend en imports ni imports relativos con puntos).
7.  **Logging y Trazabilidad:**
      * Todo error debe ser logueado con `exc_info=True`.
      * El worker debe capturar excepciones y retornarlas en el resultado del job para que la API pueda reportar "FAILED: \<razón\>" en lugar de un fallo silencioso.

## 5\. Especificaciones de Módulos

### A. Configuración `.env.example`, incluir estas variables dummy

  * `GEMINI_API_KEY=[YOUR KEY HERE]`
  * `GOOGLE_APPLICATION_CREDENTIALS=.gcp/credentials.json`
  * `PROJECT_ID=[YOUR PROJECT HERE]`
  * `BUCKET_NAME=panel-one-outputs`
  * `REDIS_URL=redis://localhost:6379`
  * `API_URL=http://localhost:8080`

### B. Configuración (`config.py`, `schemas.py`, `pyproject.toml`)

  * **config.py:**
      * Usar `pydantic_settings`.
      * **Validación Redis:** La validación de `REDIS_URL` debe permitir tanto el esquema `redis://` (local) como `rediss://` (para conexiones con SSL/TLS en producción).
      * Validar existencia física del archivo `GOOGLE_APPLICATION_CREDENTIALS` solo si se provee path.
  * **schemas.py:** Enum `JobStatus`: **`QUEUED`**, `PROCESSING_IMAGES`, `GENERATING_STORY`, `GENERATING_IMAGE`, `UPLOADING`, `COMPLETED`, `FAILED`. Incluir un campo `error_message: str | None` en el schema de respuesta del Job.
  * **pyproject.toml:**
      * **Dependencias:** Añadir `requests` y **`rich`** a las dependencias.
      * **Build System (CRÍTICO):** Incluir explícitamente la sección `[build-system]` usando `hatchling` (`requires = ["hatchling"]`, `build-backend = "hatchling.build"`) para evitar errores de construcción con `uv sync`.
      * **Targets:** Configura explícitamente la sección `[tool.hatch.build.targets.wheel]` con `packages = ["."]` para que hatchling incluya los archivos del directorio actual en el paquete.
      * **Scripts (Entry Points):** Los scripts en `[project.scripts]` deben ser Python Entry Points para permitir la ejecución limpia con `uv run`:
          * Server: `start` -\> función `start()` en `server.py` (ejecuta `uvicorn.run`).
          * Worker: `worker` -\> función `main()` en `run_worker.py`.
          * Client: `client` -\> función `app()` (Typer) en `client.py`.
  * **Manejo de Variables de Entorno:** Utilizar `load_dotenv()` de `python-dotenv` al inicio de `config.py`.
  * **Inicialización de GCS:** Al instanciar `storage.Client()`, pasa explícitamente `project=settings.PROJECT_ID`.
  * **Configuración de Arq:** En `WorkerSettings`, inicializar `redis_settings` explícitamente usando `RedisSettings.from_dsn(settings.REDIS_URL)`.

### C. Infraestructura y API (`server.py`)

  * **Puerto Dinámico (CRÍTICO Cloud Run):** Asegúrate de que `uvicorn.run` lea el puerto de la variable de entorno `PORT` (default 8080), ejemplo: `port=int(os.environ.get("PORT", 8080))`. No forzar el puerto 8080 hardcodeado.
  * **Endpoints:**
      * `GET /health`: Retorna `{"status": "ok"}` (Vital para Cloud Run checks).
      * `POST /generate`: Sube inputs a GCS, encola trabajo (estado `QUEUED`), retorna ID.
      * `WS /ws/{job_id}`: Notifica cambios. **Importante:** Usar `websocket.send_text()` enviando strings JSON puros.
      * `GET /job/{job_id}`: Polling de estado. Si el status es `FAILED`, debe incluir el mensaje de error.
  * **Middleware:** CORS permitiendo `["*"]`.
  * **Arq Pool:** Crear el pool de conexiones Arq (`create_pool`) en el evento `lifespan` de FastAPI.

### D. Worker como Servicio (`worker.py`, `run_worker.py` y `run_worker.sh`)

  * **Sintaxis de Arq (CRÍTICO):**
      * La función del trabajo **debe** ser asíncrona: `async def generate_panel(ctx, images_urls: list[str])`.
      * **Context (`ctx`):** El primer argumento debe ser siempre `ctx`.
      * **Startup/Shutdown:** Usar `on_startup` dentro de `WorkerSettings` para inicializar el cliente de Gemini y GCS **una sola vez** y guardarlos en `ctx` (ej. `ctx['gemini_client']`).
  * **GenAI Syntax & Config:**
      * Al llamar a generar imagen, **es obligatorio** usar la configuración exacta del script original:
        ```python
        types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        )
        ```
      * Usar `client.models.generate_content`.
  * **Archivo `run_worker.py`:** Debe contener una función `main()` que ejecute programáticamente el worker usando `arq.run_worker(WorkerSettings)`.
  * **Script `run_worker.sh`:** Este script se usará como Entrypoint en Docker y debe:
    1.  Levantar un servidor HTTP dummy en background en el puerto `$PORT`: `python -m http.server ${PORT:-8080} &`.
    2.  Ejecutar el worker invocando el script de python definido previamente: `exec uv run worker` (usando el alias definido en `pyproject.toml`).
  * **Lógica:** Actualiza estado a `PROCESSING_IMAGES` al iniciar ejecución real. Timeout descarga GCS: 60s. Timeout Trabajo: 590s.
  * **Manejo de Excepciones:** Envolver todo en `try/except`. Loguear traceback, actualizar estado a `FAILED` en Redis y guardar mensaje de error.

### E. Almacenamiento (`setup_gcs.py` y `storage.py`)

  * **Setup:** Usar `pydantic-settings`. Crear bucket con "Uniform Bucket Level Access" DESHABILITADO para permitir ACLs públicas.
  * **Validación de Credenciales:** Al inicio de `setup_gcs.py`, verificar si existen credenciales válidas. Si `GOOGLE_APPLICATION_CREDENTIALS` no está en `.env` (y no estamos en Cloud Run), imprimir un mensaje de error claro ("ERROR: No credentials found in .env") y salir con código de error.
  * **Configuración y Smoke Test:**
    1.  Configurar Lifecycle Rule (24h).
    2.  **Ejecutar Smoke Test (CRÍTICO):** El script debe intentar subir un archivo dummy, hacerlo público, obtener su URL, validar que sea accesible vía HTTP y finalmente borrarlo. Si esto falla, el script debe abortar.
  * **Visibilidad Pública:** Es obligatorio que cada función de subida ejecute `blob.make_public()` antes de retornar la URL.
  * **Lifecycle Rules:** Definir las reglas siempre como diccionarios puros (JSON-compatible).

### F. Cliente CLI (`client.py`)

  * **Lógica:** Replicar exactamente la funcionalidad del script original.
  * **Entrada (Argumentos):** Debe usar `Typer` y requerir obligatoriamente el argumento `--dir` (ruta al directorio de imágenes). Ejemplo de uso: `uv run client --dir inputs/`.
  * **UI/UX (Rich):** Es obligatorio usar la librería **`rich`** para toda la salida por consola:
      * Usar `rich.progress.Progress` para spinners durante la espera de estados.
      * Usar colores para mensajes de éxito (verde) o error (rojo).
      * Mantener el estilo visual "hacker/terminal" del script original.
  * **Config:** Soportar cambio fácil entre `localhost` y URL de producción mediante variables de entorno (`API_URL`).
  * **Validación Estricta:** `PIL.Image.open().verify()`.
  * **Feedback de Salida:** Imprimir URL pública de la imagen generada y ruta local.

## 6\. Deployment (Google Cloud Run)

Incluir archivos para desplegar en Google Cloud Platform:

1.  **Dockerfiles (API y Worker):**
      * **Contexto de Copia:** Copia `uv.lock` y `README.md` junto con `pyproject.toml` antes de instalar dependencias para asegurar consistencia.
      * **Comando de Ejecución (CMD):** NO uses `uv run` en el `CMD` final de la API.
          * API: `CMD ["/app/.venv/bin/python", "server.py"]`.
          * Worker: `CMD ["./run_worker.sh"]` (asegúrate de darle permisos de ejecución chmod +x en el Dockerfile).
2.  **Cloud Build (`cloudbuild.yaml`):**
      * Construir imágenes.
      * Deploy **API**:
          * Servicio público (`--allow-unauthenticated`).
          * Región: `us-central1`.
      * Deploy **Worker**: Servicio privado con configuración robusta:
          * `--no-cpu-throttling`, `--min-instances=1`, `--max-instances=5`, `--memory=2Gi`.
      * **Mapeo de Secretos:** Inyectar `GEMINI_API_KEY` y `REDIS_URL`.
      * **Autenticación GCP (CRÍTICO):** NO intentes montar `GOOGLE_APPLICATION_CREDENTIALS` como archivo/secreto en Cloud Run. Asume que el servicio usará la Identidad de Servicio (Service Account) por defecto de Cloud Run para autenticarse contra GCS y Vertex AI.
3.  **Automation Script (`deploy.sh`):**
      * Script bash ejecutable que encapsule `gcloud builds submit`.
      * Se ejecuta desde el directorio `backend/`.
      * Revisa si tiene todo lo necesario para configurar en `.env`.
      * Acceso Público Explícito: Incluir un comando gcloud run services add-iam-policy-binding después del despliegue para asignar explícitamente el rol roles/run.invoker a allUsers. Esto es clave para evitar errores 403 incluso si se usa el flag --allow-unauthenticated.
      * **Output:** Imprimir claramente la **URL pública del API**.

## 7\. Entregable

1.  Código fuente completo dentro de `backend/`.
2.  Archivos de configuración (`pyproject.toml`, Dockerfiles, Cloud Build, `deploy.sh`).
3.  **Archivo `.gitignore` Completo (ver sección 3).**
4.  **Manual (README.md):** Documentar los comandos utilizando la sintaxis limpia de scripts definida en `pyproject.toml`:
      * Setup: `uv run setup`
      * Server: `uv run start`
      * Worker Local: `uv run worker`
      * Cliente: `uv run client --dir <path>`