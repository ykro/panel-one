# Prompt: Frontend Development - Panel One

## 1\. Objetivo

Construir la interfaz de usuario para "Panel One" en el directorio `frontend/`. La aplicación debe consumir el backend existente ofreciendo una experiencia visual pulida, con alta tolerancia a fallos de red y utilizando las últimas tecnologías de React. El front debe consumir todo lo que el backend ofrece, si hay algo que el front usa que el back no tiene, aclaralo.

## 2\. Stack Tecnológico y Configuración

1.  **Framework:** Inicializar Next.js 16.0.7 o superior con React 19.2 o superior.
2.  **Librerías:** Instalar las dependencias necesarias ejecutando:
    `npm install framer-motion lucide-react clsx tailwind-merge sonner`
3.  **Entorno:** Configurar `.env.local` apuntando al backend remoto que publicamos antes(obten el url correcto).
      * `NEXT_PUBLIC_API_URL=https://[URL]`
      * `NEXT_PUBLIC_WS_URL=wss://[URL]/ws`

## 3\. Sistema de Diseño

  * **Tema:** Interfaz con una paleta de colores clara, elegante, moderna y amigable.
      * Fondo: `bg-zinc-50`.
      * Texto: `text-zinc-900` principal, `text-zinc-500` secundario.
      * Bordes: `border-zinc-200`.
  * **Estilo:** Premium. Sombras suaves, tipografía limpia (usar `next/font` para Inter) y espaciado generoso.
  * **Animaciones:** Usar `framer-motion` para transiciones suaves entre estados de carga, línea de tiempo y resultado.

## 4\. Lógica de Negocio `usePanelGenerator`

Implementar una máquina de estados basada estrictamente en la respuesta del backend.

### A. Endpoints y Comunicación

Respetar estrictamente las siguientes rutas y métodos:

  * **Subida de Archivos (`POST`):**
      * Endpoint: `/generate`
      * Body: `FormData` con campo `images` (multipart/form-data).
      * Acción: Al recibir respuesta exitosa, guardar `job_id` y conectar WebSocket.
  * **Estado del Trabajo (`GET`):**
      * Endpoint: `/job/{job_id}` (Nota: es singular `/job/`, NO `/jobs/`).
      * Uso: Polling/Watchdog.
  * **WebSocket (`WS`):**
      * Endpoint: `/ws/{job_id}`
      * Uso: Actualizaciones en tiempo real.

El cliente WebSocket en el frontend debe detectar automáticamente si la página se está sirviendo sobre HTTPS. Si es así, debe forzar el uso del protocolo seguro wss:// en lugar de ws:// para evitar errores de "Mixed Content".

Implementa una limpieza de la URL de conexión para prevenir segmentos de ruta duplicados (ej. evitar /ws/ws/ si la variable de entorno ya incluye /ws).

### B. Flujo y Estados (Case Sensitive)

Los estados se reciben en **MAYÚSCULAS**. Normalizar si es necesario para UI, pero respetar el valor crudo para la lógica:

  * Estados: `QUEUED`, `PROCESSING_IMAGES`, `GENERATING_STORY`, `GENERATING_IMAGE`, `UPLOADING`, `COMPLETED`, `FAILED`.

### C. Lógica de Resiliencia y Watchdog

  * **Mecanismo de Watchdog:** Implementar un intervalo de 5 segundos que consulte `GET /job/{job_id}`. Esto es redundancia por si el WebSocket falla.
  * **Persistencia de Sesión (Singleton):**
      * Usar `localStorage` para guardar el `job_id`.
      * Al recargar la página (mount), verificar si existe un `job_id`. Si existe, hacer un fetch a `/job/{job_id}` para recuperar el estado actual y restaurar la UI (bloqueando la UploadZone).
  * **Manejo de Errores Crítico (503/Timeout):**
      * Si el endpoint `GET /job/{job_id}` devuelve **503 Service Unavailable** o timeout, se asume que el servicio está saturado o caído.
      * **Acción obligatoria:** Mostrar mensaje de error amigable y **eliminar inmediatamente el `job_id` del localStorage** para prevenir bucles de reconexión infinita al recargar.
  * **Finalización:**
      * `COMPLETED`: Mostrar imagen usando el campo `result_url`.
      * `FAILED`: Mostrar error usando el campo `error_message` y permitir reinicio (limpiando localStorage).

## 5\. Implementación del Proxy de Descarga

Crear un **Route Handler** de Next.js en `app/api/proxy-image/route.ts`.

  * **Función:** Este endpoint debe recibir un parámetro `url`, hacer un fetch a la imagen externa (GCS) y devolverla al cliente con los headers adecuados (`Content-Disposition: attachment`) para forzar la descarga y evitar bloqueos de CORS.

## 6\. Componentes de UI `page.tsx`

### A. UploadZone

  * **Interacción:** Arrastrar y soltar archivos.
  * **Validación:** Máximo 8 archivos, solo imágenes. Mostrar alertas si no se cumple.
  * **Grid:** Mostrar miniaturas con opción de eliminar individualmente antes de enviar.

### B. ProgressTimeline

  * **Visual:** Lista vertical de pasos.
  * **Indicador:** El paso actual debe tener un icono pulsante.
  * **Mapeo de Estados:**
      * `QUEUED`: "En cola de espera..."
      * `PROCESSING_IMAGES`: "Procesando imágenes..."
      * `GENERATING_STORY`: "Generando historia..."
      * `GENERATING_IMAGE`: "Generando panel final..."
      * `UPLOADING`: "Finalizando..."

### C. ResultView

  * **Contenedor:** Marco 16:9 blanco, con bordes redondeados y sombra.
  * **Imagen:** Renderizar la propiedad `result_url` (IMPORTANTE: no usar `output_url`).
  * **Acciones:**
      * Botón Descargar que llame al Route Handler del proxy local.
      * Botón Reiniciar para limpiar el estado y comenzar de cero.

### D. ErrorState

  * **Visual:** Tarjeta simple con alerta.
  * **Datos:** Mostrar el contenido de `error_message` si está disponible.
  * **Acción:** Botón para reiniciar la aplicación.

## 7\. Definiciones de Tipo (Estricto)

Usar estas interfaces exactas basadas en la especificación del backend. **No inventar campos**.

```typescript
// Estados exactos del backend (Mayúsculas)
type JobStatus = 
  | 'QUEUED' 
  | 'PROCESSING_IMAGES' 
  | 'GENERATING_STORY' 
  | 'GENERATING_IMAGE' 
  | 'UPLOADING' 
  | 'COMPLETED' 
  | 'FAILED';

// Esquema de respuesta JSON (API REST y WebSocket)
interface JobResponse {
  job_id: string;             // UUID
  status: JobStatus;
  result_url: string | null;  // IMPORTANTE: Se llama result_url, NO output_url
  error_message: string | null;
}
```

## 8\. Restricciones de Código

  * **Directivas:** Marcar `page.tsx` y componentes interactivos con `"use client"`.
  * **Estructura:** Usar estrictamente el **App Router** (`app/`).
  * **Iconos:** Importar desde `lucide-react`.

## 9\. Deployment (Google Cloud Run)

Incluir archivos y configuraciones para desplegar el frontend en Cloud Run, asegurando la inyección correcta de variables de entorno públicas en tiempo de construcción.

1.  **Configuración Next.js (`next.config.ts`):**

      * Habilitar `output: "standalone"`.

2.  **Dockerfile (Multi-stage):**

      * Base: `node:20-alpine`.
      * **Manejo de ARGS:** Definir `ARG NEXT_PUBLIC_API_URL` y `ARG NEXT_PUBLIC_WS_URL` **antes** del `npm run build` y asignarlas a `ENV`. Esto es obligatorio para que Next.js capture las variables.
      * Usuario: `nextjs` (UID 1001).
      * Puerto: Exponer 3000.

3.  **Cloud Build (`cloudbuild.yaml`):**

      * Usar sustituciones `_NEXT_PUBLIC_API_URL` y `_NEXT_PUBLIC_WS_URL`.
      * Pasarlas como `--build-arg` al comando de docker build.
      * Ejemplo: `--build-arg NEXT_PUBLIC_API_URL=$_NEXT_PUBLIC_API_URL`.

4.  **Script de Automatización (`deploy.sh`):**

      * Leer `.env.local`.
      * Ejecutar `gcloud builds submit` con las sustituciones.
      * Incluir `chmod +x deploy.sh`.      
      * El script deploy.sh DEBE ejecutar explícitamente el comando gcloud run services add-iam-policy-binding [servicio] --member=allUsers --role=roles/run.invoker inmediatamente después del despliegue exitoso. Esto es obligatorio para garantizar el acceso público y prevenir errores de permisos."
      * Al finalizar exitosamente, obtener y mostrar en la consola la URL pública final del servicio desplegado en Cloud Run

## 10\. Entregable y Ejecución

1.  Código fuente completo en `frontend`.
2.  Route Handler para el proxy.
3.  Archivos de despliegue (`Dockerfile`, `cloudbuild.yaml`, `deploy.sh`).
4.  Comando dev: `npm run dev`.