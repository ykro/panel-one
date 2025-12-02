FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency definitions
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy source code
COPY . .

# Install project
RUN uv sync --frozen

# Environment variables
ENV PORT=8080
ENV PATH="/app/.venv/bin:$PATH"

# Run server
CMD ["/app/.venv/bin/python", "server.py"]
