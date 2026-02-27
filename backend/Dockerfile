# CBE Lesson Planner - Backend Dockerfile
# Production-ready FastAPI application for Kenyan teachers

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default port (Railway overrides via $PORT)
ENV PORT=8001
EXPOSE $PORT

# Health check (uses $PORT env variable)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; import os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", 8001)}/api/health')" || exit 1

# Run the application (Railway sets $PORT automatically)
CMD uvicorn server:app --host 0.0.0.0 --port $PORT
