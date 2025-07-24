# Stage 1: Build stage - using a Debian-based slim image for better wheel support
FROM python:3.13.5-slim-bullseye AS base

# Set environment variables for a clean environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build tools just in case a minor package still needs to compile,
# though the major ones should now use pre-compiled wheels.
# Using --no-install-recommends keeps the layer lean.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Install poetry
RUN pip install --no-cache-dir poetry

# Set the working directory
WORKDIR /app

# Copy dependency files first to leverage Docker's layer cache
COPY pyproject.toml poetry.lock* ./

# Install dependencies. This step will now be much faster.

RUN poetry config virtualenvs.create false && poetry install --no-root

# Stage 2: Final production image - also based on bullseye for consistency
FROM python:3.13.5-slim-bullseye

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends sqlite3 && \
    rm -rf /var/lib/apt/lists/*
# Copy the installed dependencies from the build stage
COPY --from=base /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=base /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy the application code
COPY ./app /app/app
# Note: The data directory is intentionally excluded to be mounted as a volume.

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "app.main:app", "-c", "./app/config/gunicorn_conf.py"]
