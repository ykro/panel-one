import os
import io
from pathlib import Path
from typing import List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Initialize Typer and Rich
app = typer.Typer()
console = Console()

# Load environment variables
# Explicitly load from the .env file in the script directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

def validate_images(directory: Path) -> List[Image.Image]:
    """
    Scans the directory for images, validates them with Pillow, 
    and returns a list of up to 8 PIL Image objects.
    """
    valid_images = []
    # Scan for images
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    files = sorted([f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in extensions])
    
    for f in files:
        try:
            # Open and verify
            with Image.open(f) as img:
                img.verify()
            
            # Re-open to return the object (verify closes the file)
            # We need to keep the file open or load it into memory. 
            # Loading into memory is safer to avoid "closed file" errors when passing to SDK.
            img = Image.open(f)
            img.load() 
            valid_images.append(img)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not open {f.name}: {e}, skipping.[/yellow]")
            continue
            
    # Limit to 8 images
    return valid_images[:8]

@app.command()
def main(directory: Path = typer.Option(..., "--dir", help="Directory containing images")):
    """
    Panel One Backend Script
    """
    if not directory.exists() or not directory.is_dir():
        console.print(f"[red]Error: Directory {directory} does not exist.[/red]")
        raise typer.Exit(code=1)

    if not API_KEY:
        console.print("[red]Error: GEMINI_API_KEY not found in environment.[/red]")
        raise typer.Exit(code=1)

    client = genai.Client(api_key=API_KEY)

    # Paths to prompts (assuming they are in the script directory)
    script_dir = Path(__file__).parent
    story_prompt_path = script_dir / "story_prompt.md"
    imagegen_prompt_path = script_dir / "imagegen_prompt.md"

    if not story_prompt_path.exists():
         console.print(f"[red]Error: {story_prompt_path} not found.[/red]")
         raise typer.Exit(code=1)
    if not imagegen_prompt_path.exists():
         console.print(f"[red]Error: {imagegen_prompt_path} not found.[/red]")
         raise typer.Exit(code=1)

    story_prompt_text = story_prompt_path.read_text(encoding="utf-8")
    imagegen_prompt_text = imagegen_prompt_path.read_text(encoding="utf-8")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Process Images
        task_imgs = progress.add_task("Processing images...", total=None)
        images = validate_images(directory)
        if not images:
             console.print("[red]No valid images found in directory.[/red]")
             raise typer.Exit(code=1)
        progress.update(task_imgs, completed=1, description=f"Found {len(images)} images.")

        # Step 2: Generate Story
        task_story = progress.add_task("Generating story...", total=None)
        
        # Input: Prompt + Images
        contents_story = [story_prompt_text] + images
        
        try:
            response_story = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=contents_story
            )
            story_text = response_story.text
            (directory / "story.txt").write_text(story_text, encoding="utf-8")
            progress.update(task_story, completed=1, description="Story generated and saved.")
        except Exception as e:
            console.print(f"[red]Error generating story: {e}[/red]")
            raise typer.Exit(code=1)

        # Step 3: Generate Image
        task_gen_img = progress.add_task("Generating panel image...", total=None)
        
        # Input: Image Prompt + Story + Original Images
        combined_text = f"{imagegen_prompt_text}\n\nCONTEXT (STORY):\n{story_text}"
        contents_image = [combined_text] + images
        
        image_config = types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        )

        try:
            response_image = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents_image,
                config=types.GenerateContentConfig(
                    image_config=image_config
                )
            )
            
            # Extract image
            # The SDK v1 usually returns the image data in the response candidates
            generated_image_bytes = None
            
            # Check if we have candidates and parts
            if response_image.candidates and response_image.candidates[0].content.parts:
                for part in response_image.candidates[0].content.parts:
                    if part.inline_data:
                        generated_image_bytes = part.inline_data.data
                        break
            
            if generated_image_bytes:
                img_out = Image.open(io.BytesIO(generated_image_bytes))
                img_out.save(directory / "panel_one_result.png")
                progress.update(task_gen_img, completed=1, description="Image generated and saved.")
            else:
                 console.print("[red]No image data found in response.[/red]")
                 # Log full response for debugging if needed, but keep it clean for user
                 raise typer.Exit(code=1)

        except Exception as e:
            console.print(f"[red]Error generating image: {e}[/red]")
            raise typer.Exit(code=1)

    console.print("[green]Process completed successfully![/green]")

if __name__ == "__main__":
    app()
