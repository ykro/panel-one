#!/bin/bash
set -e

# Check for .env
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Make sure you have configured your environment."
else
    # Export variables from .env
    set -a
    source .env
    set +a
fi

# Function to update secret
update_secret() {
    local name=$1
    local value=$2
    
    if [ -z "$value" ]; then
        echo "Warning: Value for $name is empty, skipping secret update."
        return
    fi

    echo "Updating secret $name..."
    
    # Check if secret exists
    if ! gcloud secrets describe $name &>/dev/null; then
        echo -n "$value" | gcloud secrets create $name --replication-policy="automatic" --data-file=-
    else
        echo -n "$value" | gcloud secrets versions add $name --data-file=-
    fi
}

# Update Secrets
update_secret "GEMINI_API_KEY" "$GEMINI_API_KEY"
update_secret "REDIS_URL" "$REDIS_URL"

# Generate lockfile if missing or update it
if command -v uv &> /dev/null; then
    echo "Generating/Updating uv.lock..."
    uv lock
else
    echo "Warning: 'uv' not found. Ensure uv.lock exists and is up to date."
fi

# Submit Build
echo "Submitting Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

# Ensure Public Access (Explicitly)
echo "Setting IAM policy..."
gcloud run services add-iam-policy-binding panel-one-api \
    --region us-central1 \
    --member=allUsers \
    --role=roles/run.invoker

# Get Public URL
echo "Retrieving API URL..."
API_URL=$(gcloud run services describe panel-one-api --region us-central1 --format 'value(status.url)')

echo "---------------------------------------------------"
echo "Deployment Complete!"
echo "API URL: $API_URL"
echo "---------------------------------------------------"
