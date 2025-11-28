# Panel One

**Panel One** is a project designed to generate narrative stories and visual panels from a set of input images using Google's Gemini AI.

![Panel One Sample](script/sample_output/panel_one_result.png)

## Project Structure

This repository is organized into the following components:

### Backend / Script
Located in `script/`.
This is a Python-based CLI tool that handles the core logic:
1.  **Ingestion**: Validates and processes input images.
2.  **Storytelling**: Generates a story based on the images using `gemini-3-pro-preview`.
3.  **Visualization**: Generates a final "Panel One" image using `gemini-3-pro-image-preview`.

[Read the Backend Documentation](script/README.md) for installation and usage instructions.

### Frontend
*(Coming Soon)*
Details about the frontend application will be added here.

## Getting Started

To try out the backend script immediately:

1.  Clone this repository.
2.  Follow the setup instructions in [script/README.md](script/README.md).
