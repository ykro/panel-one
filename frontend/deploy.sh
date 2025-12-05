#!/bin/bash

# Load env vars
if [ -f .env.local ]; then
  # Use grep to remove empty lines or comments if needed
  # export $(grep -v '^#' .env.local | xargs)
  # Safer way for values with spaces potentially:
  source .env.local
fi

echo "Deploying with API URL: $NEXT_PUBLIC_API_URL"

gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL",_NEXT_PUBLIC_WS_URL="$NEXT_PUBLIC_WS_URL"

if [ $? -eq 0 ]; then
  echo "Deployment successful!"
  # Get the URL
  URL=$(gcloud run services describe panel-one-frontend --platform managed --region us-central1 --format 'value(status.url)')
  echo "Service URL: $URL"
else
  echo "Deployment failed."
  exit 1
fi
