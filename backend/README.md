# Panel One Backend

Robust backend for Panel One using FastAPI, Arq, and Google Cloud Platform.

## Setup

1.  **Install uv**: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
2.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in the values.
    ```bash
    cp .env.example .env
    ```
3.  **Install Dependencies**:
    ```bash
    uv sync
    ```
4.  **GCS Setup**:
    Initialize the Google Cloud Storage bucket and verify access.
    ```bash
    uv run setup
    ```

## Running Locally

### 1. Start Redis
Ensure you have a Redis instance running.
```bash
redis-server
```

### 2. Start API Server
```bash
uv run start
```
The API will be available at `http://localhost:8080`.

### 3. Start Worker
```bash
uv run worker
```

### 4. Run Client
Run the CLI client to process images.
```bash
uv run client --dir path/to/images
```

## Deployment

### Prerequisites
- Google Cloud SDK (`gcloud`) installed and authenticated.
- Project ID set in `gcloud config`.
- Secrets `GEMINI_API_KEY` and `REDIS_URL` created in Secret Manager.

### Deploy
Run the deployment script:
```bash
./deploy.sh
```
This will build the Docker images and deploy the API and Worker services to Cloud Run.
