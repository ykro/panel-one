import asyncio
import os
import shutil
import uuid
from pathlib import Path
from typing import List
import traceback

from arq import Worker
from arq.connections import RedisSettings
from google import genai
from google.genai import types
from PIL import Image

from config import settings
from schemas import JobStatus
from storage import download_file, upload_from_filename, delete_file
from utils import logger

# Constants
STORY_MODEL = "gemini-3-pro-preview"
IMAGE_MODEL = "gemini-3-pro-image-preview"

async def startup(ctx):
    logger.info("Worker starting up")
    ctx['gemini_client'] = genai.Client(api_key=settings.GEMINI_API_KEY)
    # We can also store the redis pool if needed, but ctx['redis'] is available if using Arq's pool?
    # Arq passes a redis connection in ctx? No, ctx['redis'] is usually the pool if configured.
    # Actually Arq creates the pool.
    pass

async def shutdown(ctx):
    logger.info("Worker shutting down")

async def update_job_status(ctx, job_id: str, status: JobStatus, result_url: str = None, error_message: str = None):
    redis = ctx['redis']
    # We store status in a separate key or hash to allow the API to query it easily
    # alongside the Arq job status.
    # Let's use a hash: job:{job_id} -> {status: ..., error: ...}
    key = f"job:{job_id}"
    data = {"status": status.value}
    if error_message:
        data["error_message"] = error_message
    if result_url:
        data["result_url"] = result_url
    
    await redis.hset(key, mapping=data)
    # Set expire to clean up eventually (e.g., 24h)
    await redis.expire(key, 86400)
    logger.info("Job status updated", job_id=job_id, status=status.value)

async def generate_panel(ctx, images_urls: List[str]):
    job_id = ctx['job_id']
    logger.info("Starting generate_panel", job_id=job_id, num_images=len(images_urls))
    
    await update_job_status(ctx, job_id, JobStatus.PROCESSING_IMAGES)
    
    tmp_dir = Path(f"/tmp/{job_id}")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    local_images = []
    
    try:
        # 1. Download Images
        download_tasks = []
        for i, url in enumerate(images_urls):
            ext = url.split('.')[-1]
            dest = tmp_dir / f"input_{i}.{ext}"
            local_images.append(dest)
            download_tasks.append(download_file(url, str(dest)))
        
        # Timeout 60s for downloads
        await asyncio.wait_for(asyncio.gather(*download_tasks), timeout=60.0)
        
        # Validate Images
        valid_pil_images = []
        for img_path in local_images:
            try:
                with Image.open(img_path) as img:
                    img.verify()
                
                # Re-open for use
                img = Image.open(img_path)
                img.load()
                valid_pil_images.append(img)
            except Exception as e:
                logger.warning("Invalid image", path=str(img_path), error=str(e))
                # We continue if at least one is valid? Or fail?
                # Script logic: "skipping". If no valid images, raise.
        
        if not valid_pil_images:
            raise ValueError("No valid images found")

        # 2. Generate Story
        await update_job_status(ctx, job_id, JobStatus.GENERATING_STORY)
        
        client: genai.Client = ctx['gemini_client']
        
        # Read prompts
        # Assuming prompts are in the current working directory (backend/)
        story_prompt = Path("story_prompt.md").read_text(encoding="utf-8")
        imagegen_prompt = Path("imagegen_prompt.md").read_text(encoding="utf-8")
        
        contents_story = [story_prompt] + valid_pil_images
        
        # Async call to Gemini? The SDK v1 might be sync or async.
        # client.models.generate_content is sync?
        # "Envolver llamadas IO (GCS/GenAI) en asyncio.to_thread"
        
        def _call_story():
            return client.models.generate_content(
                model=STORY_MODEL,
                contents=contents_story
            )
            
        response_story = await asyncio.to_thread(_call_story)
        story_text = response_story.text
        
        # 3. Generate Image
        await update_job_status(ctx, job_id, JobStatus.GENERATING_IMAGE)
        
        combined_text = f"{imagegen_prompt}\n\nCONTEXT (STORY):\n{story_text}"
        contents_image = [combined_text] + valid_pil_images
        
        image_config = types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        )
        
        def _call_image():
            return client.models.generate_content(
                model=IMAGE_MODEL,
                contents=contents_image,
                config=types.GenerateContentConfig(
                    image_config=image_config
                )
            )

        response_image = await asyncio.to_thread(_call_image)
        
        # Extract image
        generated_image_bytes = None
        if response_image.candidates and response_image.candidates[0].content.parts:
            for part in response_image.candidates[0].content.parts:
                if part.inline_data:
                    generated_image_bytes = part.inline_data.data
                    break
        
        if not generated_image_bytes:
            raise ValueError("No image data found in response")
            
        # Save to tmp
        output_path = tmp_dir / "output.png"
        # Write bytes
        with open(output_path, "wb") as f:
            f.write(generated_image_bytes)
            
        # 4. Upload Result
        await update_job_status(ctx, job_id, JobStatus.UPLOADING)
        
        result_url = await upload_from_filename(
            str(output_path), 
            f"outputs/{job_id}/panel.png", 
            content_type="image/png"
        )
        
        # 5. Cleanup Input Files (GCS)
        # "Elimina archivos de input de GCS tras completar o fallar"
        # We do this in finally block or here?
        # Let's do it here for success path, and catch block for failure path.
        cleanup_tasks = [delete_file(url) for url in images_urls]
        await asyncio.gather(*cleanup_tasks)
        
        await update_job_status(ctx, job_id, JobStatus.COMPLETED, result_url)
        return result_url

    except Exception as e:
        logger.error("Job failed", job_id=job_id, exc_info=True)
        error_msg = str(e)
        await update_job_status(ctx, job_id, JobStatus.FAILED, error_message=error_msg)
        
        # Attempt cleanup on failure too
        try:
            cleanup_tasks = [delete_file(url) for url in images_urls]
            await asyncio.gather(*cleanup_tasks)
        except Exception:
            pass
            
        # Return error info so Arq knows it failed (though we handled it gracefully for our status)
        # Spec: "El worker debe capturar excepciones y retornarlas en el resultado del job"
        # If we raise, Arq marks it as failed.
        # But we also want to set our custom status.
        # Let's return the error dict.
        return {"error": error_msg}
        
    finally:
        # Cleanup local tmp
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

class WorkerSettings:
    functions = [generate_panel]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    # Job timeout 590s
    job_timeout = 590
