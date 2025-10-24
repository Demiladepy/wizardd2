FROM python:3.13-slim-bookworm

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /bin/uv

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        curl \
        gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_HTTP_TIMEOUT=120

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --locked --no-install-project

# Copy application code
COPY . .

# Install the application
RUN uv sync --locked

# Expose port
EXPOSE 8000

# Start the application
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]