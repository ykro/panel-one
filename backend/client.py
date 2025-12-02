import os
import time
import requests
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from PIL import Image
from dotenv import load_dotenv

# Load env
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8080")

app = typer.Typer()
console = Console()

def validate_images(directory: Path) -> List[Path]:
    """
    Scans the directory for images, validates them with Pillow, 
    and returns a list of valid image paths.
    """
    valid_images = []
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    if not directory.exists():
        return []
        
    files = sorted([f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in extensions])
    
    for f in files:
        try:
            with Image.open(f) as img:
                img.verify()
            valid_images.append(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not open {f.name}: {e}, skipping.[/yellow]")
            continue
            
    return valid_images[:8]

@app.command()
def main(directory: Path = typer.Option(..., "--dir", help="Directory containing images")):
    """
    Panel One Backend Client
    """
    if not directory.exists() or not directory.is_dir():
        console.print(f"[red]Error: Directory {directory} does not exist.[/red]")
        raise typer.Exit(code=1)

    # 1. Validate Images
    console.print(f"Scanning {directory}...")
    images = validate_images(directory)
    if not images:
        console.print("[red]No valid images found in directory.[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"[green]Found {len(images)} valid images.[/green]")

    # 2. Submit Job
    files = []
    opened_files = []
    try:
        for img_path in images:
            f = open(img_path, "rb")
            opened_files.append(f)
            # requests expects ('field_name', (filename, file_obj, content_type))
            files.append(('images', (img_path.name, f, f"image/{img_path.suffix[1:]}")))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task_submit = progress.add_task("Uploading images and submitting job...", total=None)
            
            try:
                response = requests.post(f"{API_URL}/generate", files=files)
                response.raise_for_status()
                job_data = response.json()
                job_id = job_data["job_id"]
                progress.update(task_submit, completed=1, description="Job submitted successfully.")
            except Exception as e:
                progress.update(task_submit, completed=1, description="[red]Failed to submit job.[/red]")
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(code=1)

            # 3. Poll Status
            task_status = progress.add_task("Waiting for worker...", total=None)
            
            while True:
                try:
                    resp = requests.get(f"{API_URL}/job/{job_id}")
                    resp.raise_for_status()
                    data = resp.json()
                    status = data["status"]
                    
                    # Update description based on status
                    description = f"Status: {status}"
                    if status == "QUEUED":
                        description = "Queued..."
                    elif status == "PROCESSING_IMAGES":
                        description = "Processing images..."
                    elif status == "GENERATING_STORY":
                        description = "Generating story..."
                    elif status == "GENERATING_IMAGE":
                        description = "Generating panel image..."
                    elif status == "UPLOADING":
                        description = "Uploading result..."
                    
                    progress.update(task_status, description=description)
                    
                    if status == "COMPLETED":
                        progress.update(task_status, completed=1, description="Job completed!")
                        result_url = data.get("result_url")
                        break
                    elif status == "FAILED":
                        error_msg = data.get("error_message", "Unknown error")
                        progress.update(task_status, completed=1, description=f"[red]Job failed: {error_msg}[/red]")
                        raise typer.Exit(code=1)
                    
                    time.sleep(1)
                except KeyboardInterrupt:
                    console.print("[yellow]Cancelled by user.[/yellow]")
                    raise typer.Exit(code=1)
                except Exception as e:
                    # Ignore transient network errors?
                    pass
                    time.sleep(1)

    finally:
        for f in opened_files:
            f.close()

    # 4. Download Result
    if result_url:
        console.print(f"[green]Result URL: {result_url}[/green]")
        try:
            local_path = directory / "panel_one_result.png"
            console.print(f"Downloading to {local_path}...")
            r = requests.get(result_url)
            r.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(r.content)
            console.print(f"[green]Saved to {local_path}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to download result: {e}[/red]")

if __name__ == "__main__":
    app()
