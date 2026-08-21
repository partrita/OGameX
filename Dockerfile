# High-performance Python container with uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project specifications and lockfile for caching
COPY pyproject.toml uv.lock README.md /app/

# Install dependencies using uv
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY python /app/python

# Install the project
RUN uv sync --frozen --no-dev

ENV PYTHONPATH=/app

EXPOSE 8000

# Run FastAPI app directly via uv
CMD ["uv", "run", "--no-sync", "uvicorn", "python.app.main:app", "--host", "0.0.0.0", "--port", "8000"]