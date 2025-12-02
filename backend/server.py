import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job
import uvicorn

from config import settings
from schemas import JobStatus, JobResponse
from storage import upload_file
from utils import configure_logging, logger

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up API")
    app.state.redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    yield
    logger.info("Shutting down API")
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/generate", response_model=JobResponse)
async def generate(images: List[UploadFile] = File(...)):
    job_id = str(uuid.uuid4())
    logger.info("Received generate request", job_id=job_id, num_images=len(images))
    
    # Upload images to GCS
    gcs_urls = []
    try:
        upload_tasks = []
        for i, img in enumerate(images):
            ext = img.filename.split('.')[-1] if '.' in img.filename else "png"
            blob_name = f"inputs/{job_id}/image_{i}.{ext}"
            # We need to read the file content
            # UploadFile exposes a SpooledTemporaryFile
            upload_tasks.append(upload_file(img.file, blob_name, img.content_type))
        
        gcs_urls = await asyncio.gather(*upload_tasks)
        
    except Exception as e:
        logger.error("Failed to upload images", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to upload images: {str(e)}")

    # Enqueue Job
    redis = app.state.redis
    await redis.enqueue_job('generate_panel', gcs_urls, _job_id=job_id)
    
    # Set initial status
    await redis.hset(f"job:{job_id}", mapping={"status": JobStatus.QUEUED.value})
    
    return JobResponse(job_id=job_id, status=JobStatus.QUEUED)

@app.get("/job/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    redis = app.state.redis
    
    # Check custom status
    data = await redis.hgetall(f"job:{job_id}")
    if not data:
        # Check if it exists in Arq?
        try:
            job = Job(job_id, redis)
            status = await job.status()
            if status == 'not_found':
                 raise HTTPException(status_code=404, detail="Job not found")
            # Map Arq status to our status if custom key missing?
            # Usually custom key should exist if we created it.
            # If missing, maybe expired?
            return JobResponse(job_id=job_id, status=JobStatus.FAILED, error_message="Job data expired or missing")
        except Exception:
             raise HTTPException(status_code=404, detail="Job not found")

    status_str = data.get(b'status', b'').decode('utf-8')
    error_msg = data.get(b'error_message', b'').decode('utf-8') if b'error_message' in data else None
    result_url = data.get(b'result_url', b'').decode('utf-8') if b'result_url' in data else None
    
    return JobResponse(
        job_id=job_id, 
        status=JobStatus(status_str), 
        error_message=error_msg or None,
        result_url=result_url or None
    )

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    redis = app.state.redis
    last_status = None
    
    try:
        while True:
            data = await redis.hgetall(f"job:{job_id}")
            if data:
                status_str = data.get(b'status', b'').decode('utf-8')
                error_msg = data.get(b'error_message', b'').decode('utf-8') if b'error_message' in data else None
                result_url = data.get(b'result_url', b'').decode('utf-8') if b'result_url' in data else None
                
                current_response = JobResponse(
                    job_id=job_id,
                    status=JobStatus(status_str),
                    error_message=error_msg or None,
                    result_url=result_url or None
                )
                
                if status_str != last_status:
                    await websocket.send_text(current_response.model_dump_json())
                    last_status = status_str
                
                if status_str in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
                    break
            else:
                # Job not found yet?
                pass
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", job_id=job_id)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        await websocket.close()

def start():
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    start()
