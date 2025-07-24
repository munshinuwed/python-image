# Stage 1: Use the official Python image as a base
FROM python:3.13.5-alpine AS base

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache build-base
# Install poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy only the dependency files to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install dependencies, but not the project itself
# --no-root prevents installing the project itself, which we will copy later
# --no-dev installs only production dependencies
RUN poetry install --no-root --no-dev

# Stage 2: Create the final production image
FROM python:3.13.5-alpine

WORKDIR /app

# Copy the installed dependencies from the base stage
COPY --from=base /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=base /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy the application code
COPY ./app /app/app
COPY ./app/data /app/data

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Gunicorn as a process manager
# This starts 4 worker processes, each running a Uvicorn instance.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.api:app", "--bind", "0.0.0.0:8000"]
