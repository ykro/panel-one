from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING_IMAGES = "PROCESSING_IMAGES"
    GENERATING_STORY = "GENERATING_STORY"
    GENERATING_IMAGE = "GENERATING_IMAGE"
    UPLOADING = "UPLOADING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    result_url: Optional[str] = None
    error_message: Optional[str] = None

class GenerateRequest(BaseModel):
    pass # Inputs are handled via multipart/form-data, so this might be empty or used for other params
