import asyncio
from google.cloud import storage
from config import settings
from utils import logger
import os

def get_client():
    return storage.Client(project=settings.PROJECT_ID)

async def upload_file(file_obj, destination_blob_name: str, content_type: str) -> str:
    """
    Uploads a file-like object to GCS and makes it public.
    Returns the public URL.
    """
    client = get_client()
    bucket = client.bucket(settings.BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    def _upload():
        blob.upload_from_file(file_obj, content_type=content_type)
        blob.make_public()
        return blob.public_url

    return await asyncio.to_thread(_upload)

async def upload_from_filename(filename: str, destination_blob_name: str, content_type: str = None) -> str:
    """
    Uploads a file from disk to GCS and makes it public.
    Returns the public URL.
    """
    client = get_client()
    bucket = client.bucket(settings.BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    def _upload():
        blob.upload_from_filename(filename, content_type=content_type)
        blob.make_public()
        return blob.public_url

    return await asyncio.to_thread(_upload)

async def download_file(gcs_url: str, destination_path: str):
    """
    Downloads a file from a GCS URL to a local path.
    Assumes URL structure: https://storage.googleapis.com/BUCKET_NAME/BLOB_NAME
    """
    # Parse blob name from URL
    # Example: https://storage.googleapis.com/panel-one-outputs/inputs/123/image.png
    # or https://storage.googleapis.com/download/storage/v1/b/panel-one-outputs/o/inputs%2F123%2Fimage.png...
    
    # Simple parsing assuming standard public URL format
    prefix = f"https://storage.googleapis.com/{settings.BUCKET_NAME}/"
    if not gcs_url.startswith(prefix):
        # Fallback for other URL formats if necessary, or assume it's just the blob path if passed internally?
        # The spec says "URLs de GCS".
        # Let's try to handle the standard public URL.
        raise ValueError(f"Invalid GCS URL: {gcs_url}")

    blob_name = gcs_url[len(prefix):]
    
    client = get_client()
    bucket = client.bucket(settings.BUCKET_NAME)
    blob = bucket.blob(blob_name)

    def _download():
        blob.download_to_filename(destination_path)

    await asyncio.to_thread(_download)

async def delete_file(gcs_url: str):
    """
    Deletes a file from GCS given its URL.
    """
    prefix = f"https://storage.googleapis.com/{settings.BUCKET_NAME}/"
    if not gcs_url.startswith(prefix):
        logger.warning("Skipping delete, invalid URL", url=gcs_url)
        return

    blob_name = gcs_url[len(prefix):]
    client = get_client()
    bucket = client.bucket(settings.BUCKET_NAME)
    blob = bucket.blob(blob_name)

    def _delete():
        try:
            blob.delete()
        except Exception as e:
            logger.warning("Failed to delete blob", blob=blob_name, error=str(e))

    await asyncio.to_thread(_delete)
