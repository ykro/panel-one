# Panel One Backend Script

Este script de Python gestiona el backend de "Panel One", utilizando la API de Google GenAI para generar historias e imágenes basadas en un conjunto de imágenes de entrada.

## Requisitos Previos

1.  **Python 3.12+** (Gestionado por `uv`)
2.  **uv**: Gestor de paquetes de Python. [Instalación de uv](https://github.com/astral-sh/uv).
3.  **API Key**: Una clave de API de Google Gemini configurada en un archivo `.env` como `GEMINI_API_KEY`.

## Instalación

1.  Navega al directorio `script/`:
    ```bash
    cd script
    ```

2.  Instala las dependencias:
    ```bash
    uv sync
    ```
    (O si acabas de inicializar, `uv add google-genai python-dotenv typer rich pillow`)

## Estructura de Archivos Esperada

El script asume la siguiente estructura de directorios:

```
panel-one/
├── .env                  # Archivo con GEMINI_API_KEY
├── story_prompt.md       # Prompt para la historia
├── imagegen_prompt.md    # Prompt para la generación de imagen
└── script/
    ├── main.py           # Este script
    ├── pyproject.toml    # Configuración de uv
    └── uv.lock
```

## Uso

Para ejecutar el script, utiliza `uv run` pasando el argumento `--dir` con la ruta al directorio que contiene las imágenes de entrada.

```bash
uv run main.py --dir /ruta/a/tus/imagenes
```

### Ejemplo:

```bash
uv run main.py --dir ../input_images
```

## Flujo de Trabajo

1.  **Validación**: El script escanea el directorio especificado buscando imágenes (`.jpg`, `.jpeg`, `.png`, `.webp`), valida que sean legibles y selecciona hasta 8.
2.  **Generación de Historia**: Utiliza el modelo `gemini-3-pro-preview` con `story_prompt.md` y las imágenes para crear una narrativa. Se guarda en `[dir]/story.txt`.
3.  **Generación de Imagen**: Utiliza el modelo `gemini-3-pro-image-preview` con `imagegen_prompt.md`, la historia generada y las imágenes originales para crear una nueva imagen (Panel One). Se guarda en `[dir]/panel_one_result.png`.

## Salida

En el directorio especificado (`--dir`), se generarán:

*   `story.txt`: La historia generada.
*   `panel_one_result.png`: La imagen generada.
