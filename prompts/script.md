Python script
# Objetivo
Crear y configurar un script de Python (`main.py`) para el backend de "Panel One", gestionando todo el entorno con **`uv`**. Usa un nuevo directorio "script/"

# Contexto Técnico
1. **Gestor de Paquetes:** Se utiliza **`uv`**.
2. **Biblioteca AI:** `google-genai` (SDK v1). **NO** usar `google-generativeai`.
3. **Manejo de Imágenes:** Utilizar **Pillow (PIL)** para cargar y procesar los archivos de imagen antes de enviarlos a la API.
4. **Seguridad:** API Key desde `.env` (`GEMINI_API_KEY`).
5. **Prompts Externos:** El script debe leer `story_prompt.md` y `imagegen_prompt.md` del mismo directorio

# Acciones de Configuración 
**No listes los comandos, ejecútalos usando tu herramienta de terminal:**
1. Si no existe, inicializa el proyecto: `uv init`.
2. Instala las dependencias: `uv add google-genai python-dotenv typer rich pillow`.

# Especificaciones del Código (`main.py`)

## 1. Entrada (CLI)
- Usar `typer`.
- Argumento obligatorio: `--dir` (ruta al directorio).

## 2. Procesamiento (Solo Imágenes)
- Escanear `--dir` buscando solo `.jpg`, `.jpeg`, `.png`, `.webp`.
- **Validación con Pillow:** Intentar abrir los archivos con `PIL.Image` para confirmar que son imágenes válidas.
- **Límite:** Máximo 8 imágenes. Si hay más, tomar las primeras 8.
- **Output:** Crear una lista de objetos `PIL.Image` (o los bytes leídos) listos para enviar a la API.

## 3. Flujo IA (Secuencial)

### Paso 1: Generación de Historia
- **Modelo:** `gemini-3-pro-preview`.
- **Input (`contents`):** Debe incluir el texto de `story_prompt.md` **Y** la lista de imágenes procesadas.
- **Acción:** Generar historia narrativa.

### Paso 2: Visualización (Generación de Imagen)
- **Modelo:** `gemini-3-pro-image-preview`.
- **Input (`contents`):** Debe incluir el texto combinado (Contenido de `imagegen_prompt.md` + Historia generada en Paso 1) **Y TAMBIÉN** la lista de imágenes originales (para referencia de estilo/personaje).
- **Parámetros de Configuración:** Debes utilizar image_config para asegurar los siguientes requisitos:
    types.ImageConfig(
                aspect_ratio="16:9,
                image_size="2K"
    )  

- **SINTAXIS OBLIGATORIA:** Para generar la imagen, utiliza el método `client.models.generate_content`. Asegúrate de pasar el prompt de texto, las imágenes en `contents`, y el objeto de configuración con los parámetros de aspect ratio.

## 4. Salida
- **Consola:** Usar `rich` para mostrar el progreso.
- **Archivos:**
  - `story.txt`: Guardar la historia en el directorio `--dir`.
  - `panel_one_result.png`: Guardar la imagen generada en el directorio `--dir`. (Nota: Verifica la estructura de la respuesta del objeto `generate_content` para extraer y guardar correctamente los bytes de la imagen generada).

# Entregable
1. Entorno configurado con `uv`.
2. Código completo de `main.py` funcional.
3. README detallado con instrucciones de instalación y uso