#!/bin/bash
set -e

# Start dummy HTTP server for Cloud Run health checks
PORT=${PORT:-8080}
echo "Starting dummy HTTP server on port $PORT"
python -m http.server $PORT &

# Start the worker
echo "Starting worker..."
exec uv run worker
