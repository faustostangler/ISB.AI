# Stage 0: Base stage
FROM python:3.13-slim-bookworm AS base

# Stage 1: Build stage
FROM base AS builder
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Install dependencies
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy only necessary files for installation
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime stage
FROM base AS final

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Install system dependencies (ffmpeg is useful for audio scribe tools like Whisper and yt-dlp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Add .venv/bin to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY src /app/src
COPY README.md /app/README.md

# Set environment variables
ENV PYTHONPATH="/app/src"

# Default command
CMD ["python", "-m", "isb.main"]
