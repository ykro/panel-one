# Panel One

**Panel One** is a project designed to generate narrative stories and visual panels from a set of input images using Google's Gemini AI.

![Panel One Sample](script/sample_output/panel_one_result.png)

### Sample Story Output

**Concepto:** La rutina de comedia se transforma literalmente en una escalada épica, visualizando el esfuerzo del artista como una conquista de la naturaleza, culminando en la celebración.

**Viñeta 1:**
Plano medio americano. El protagonista (hombre con gafas, barba, camisa azul) está de pie en un escenario de club de comedia con iluminación dramática azul y morada. Sostiene el micrófono con fuerza, gesticulando con la mano izquierda abierta. Detrás de él, el cartel de "Stand Up Comedy" comienza a distorsionarse y derretirse; el suelo de madera del escenario empieza a transformarse en roca volcánica gris y áspera bajo sus botas.

**Viñeta 2:**
Plano contrapicado dinámico. La transformación ha avanzado. El protagonista está a mitad de una escalada empinada, su ropa ha cambiado a una camiseta técnica morada y casco blanco, pero aún sostiene el micrófono en una mano como si fuera un piolet (herramienta de escalada). El humo del escenario se ha convertido en nubes de azufre y vapor volcánico real que lo envuelven. La iluminación es una mezcla de focos de escenario y luz solar dura de alta montaña.

**Viñeta 3:**
Plano general majestuoso. El protagonista alcanza la cima del volcán masivo. Está de pie con los brazos abiertos en señal de victoria (pose de la foto de montaña), vistiendo el equipo de escalada completo. El cráter del volcán frente a él no expulsa lava, sino que emana una luz dorada brillante y confeti, simbolizando las risas del público. El paisaje es épico, con nubes bajas y un cielo azul intenso.

**Viñeta 4:**
Primer plano (Close-up) con transición de enfoque. El protagonista ya no está en la montaña, sino en un interior cálido y moderno, vistiendo una chaqueta naranja acolchada. Sostiene una copa de vino tinto frente a su ojo derecho, mirando a través del cristal y sonriendo. Dentro del líquido del vino, en lugar de un reflejo normal, se ve reflejada la silueta de la montaña humeante que acaba de conquistar.

**Viñeta 5:**
Plano medio, ángulo frontal. El protagonista baja la copa de vino como en un brindis hacia el espectador ("Cheers"). La iluminación es suave y cálida, de restaurante nocturno. Su expresión es de satisfacción relajada. Detrás de él, a través de una ventana de vidrio, se ve una fusión onírica: las luces de la ciudad se mezclan con las estrellas sobre la silueta del volcán a lo lejos, cerrando el ciclo de la aventura.


## Project Structure

This repository is organized into the following components:

### Scripts
Located in `script/`.
This is a Python-based CLI tool that handles the core logic:
1.  **Ingestion**: Validates and processes input images.
2.  **Storytelling**: Generates a story based on the images using `gemini-3-pro-preview`.
3.  **Visualization**: Generates a final "Panel One" image using `gemini-3-pro-image-preview`.

[Read the Scripts Documentation](script/README.md) for installation and usage instructions.

### Backend
Located in `backend/`.
A robust, asynchronous backend service built with FastAPI, Arq, and Google Cloud Platform.
Key features:
- **API**: FastAPI service for job submission and status polling.
- **Worker**: Asynchronous worker using Arq and Redis for processing heavy AI tasks.
- **Storage**: Google Cloud Storage integration for handling inputs and outputs.
- **Deployment**: Ready for Google Cloud Run (Service & Worker).

[Read the Backend Documentation](backend/README.md) for setup, local development, and deployment instructions.

### Frontend
*(Coming Soon)*
Details about the frontend application will be added here.

## Getting Started

To try out the scripts immediately:

1.  Clone this repository.
2.  Follow the setup instructions in [script/README.md](script/README.md).
