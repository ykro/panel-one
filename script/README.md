# Panel One Backend Script

This Python script manages the "Panel One" backend, utilizing the Google GenAI API to generate stories and images based on a set of input images.



## Prerequisites

1.  **Python 3.12+** (Managed by `uv`)
2.  **uv**: Python package manager. [Install uv](https://github.com/astral-sh/uv).
3.  **API Key**: A Google Gemini API key configured in a `.env` file as `GEMINI_API_KEY`.

## Installation

1.  Navigate to the `script/` directory:
    ```bash
    cd script
    ```

2.  Install dependencies:
    ```bash
    uv sync
    ```

## Expected File Structure

The script assumes the following directory structure:

```
panel-one/
├── .env                  # File containing GEMINI_API_KEY
├── .gitignore
├── script/
│   ├── sample_output/    # Sample output files
│   ├── imagegen_prompt.md # Prompt for image generation
│   ├── main.py           # This script
│   ├── pyproject.toml    # uv configuration
│   ├── README.md         # This file
│   ├── story_prompt.md   # Prompt for story generation
│   └── uv.lock
```

## Usage

To run the script, use `uv run` passing the `--dir` argument with the path to the directory containing the input images.

```bash
uv run main.py --dir /path/to/your/images
```

### Example:

```bash
uv run main.py --dir ../input_images
```

## Workflow

1.  **Validation**: Scans the specified directory for images (`.jpg`, `.jpeg`, `.png`, `.webp`), validates they are readable, and selects up to 8.
2.  **Story Generation**: Uses the `gemini-3-pro-preview` model with `story_prompt.md` and the images to create a narrative. Saved to `[dir]/story.txt`.
3.  **Image Generation**: Uses the `gemini-3-pro-image-preview` model with `imagegen_prompt.md`, the generated story, and the original images to create a new image (Panel One). Saved to `[dir]/panel_one_result.png`.

## Output

In the specified directory (`--dir`), the following will be generated:

*   `story.txt`: The generated story.
*   `panel_one_result.png`: The generated image.
