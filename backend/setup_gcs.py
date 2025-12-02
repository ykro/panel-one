import sys
import os
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden
import requests
from config import settings
from utils import configure_logging, logger

configure_logging()

def main():
    # 1. Validate Credentials
    if not settings.GOOGLE_APPLICATION_CREDENTIALS and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        # Check if we are in Cloud Run (metadata server available) or have default creds?
        # Spec says: "Si GOOGLE_APPLICATION_CREDENTIALS no está en .env (y no estamos en Cloud Run), imprimir un mensaje de error claro... y salir"
        # We can check for a common Cloud Run env var like K_SERVICE
        if not os.getenv("K_SERVICE"):
             # Try to see if we can get default credentials, but spec is specific about the message if env var is missing.
             # However, the config.py loads .env.
             # If it's still None, then it's missing.
             logger.error("ERROR: No credentials found in .env")
             sys.exit(1)

    logger.info("Initializing GCS Setup", project_id=settings.PROJECT_ID, bucket=settings.BUCKET_NAME)

    try:
        client = storage.Client(project=settings.PROJECT_ID)
    except Exception as e:
        logger.error("Failed to create storage client", error=str(e))
        sys.exit(1)

    # 2. Create Bucket / Update Config
    try:
        bucket = client.bucket(settings.BUCKET_NAME)
        if not bucket.exists():
            logger.info("Creating bucket", bucket=settings.BUCKET_NAME)
            bucket.create(location="US") # Default location
        else:
            logger.info("Bucket exists", bucket=settings.BUCKET_NAME)
            bucket = client.get_bucket(settings.BUCKET_NAME)
        
        # Disable Uniform Bucket Level Access to allow fine-grained ACLs (public)
        if bucket.iam_configuration.uniform_bucket_level_access_enabled:
            logger.info("Disabling Uniform Bucket Level Access")
            bucket.iam_configuration.uniform_bucket_level_access_enabled = False
            bucket.patch()

        # Lifecycle Rule (24h)
        # "Definir las reglas siempre como diccionarios puros"
        lifecycle_rules = [
            {
                "action": {"type": "Delete"},
                "condition": {"age": 1}
            }
        ]
        bucket.lifecycle_rules = lifecycle_rules
        bucket.patch()
        logger.info("Lifecycle rules updated")

    except Exception as e:
        logger.error("Failed to configure bucket", error=str(e))
        sys.exit(1)

    # 3. Smoke Test
    logger.info("Running Smoke Test")
    blob_name = "smoke_test.txt"
    blob = bucket.blob(blob_name)
    try:
        # Upload
        blob.upload_from_string("smoke test content", content_type="text/plain")
        
        # Make Public
        blob.make_public()
        public_url = blob.public_url
        logger.info("File uploaded and made public", url=public_url)

        # Check Access
        resp = requests.get(public_url)
        if resp.status_code != 200 or resp.text != "smoke test content":
            logger.error("Smoke test failed: Could not access public file", status=resp.status_code)
            sys.exit(1)
        
        logger.info("Public access verified")

        # Delete
        blob.delete()
        logger.info("Smoke test file deleted")
        logger.info("Smoke Test PASSED")

    except Exception as e:
        logger.error("Smoke Test FAILED", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
