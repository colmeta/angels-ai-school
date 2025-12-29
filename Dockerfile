# Angels AI School - Enterprise Operating System
# Production Dockerfile

# Base Image
FROM python:3.10-slim

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Work Directory
WORKDIR $APP_HOME

# System Dependencies (for Postgres, GCC, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY . .

# Expose Port
EXPOSE 8000

# Run Application (using Gunicorn for production)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "api.main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
