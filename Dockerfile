FROM python:3.11-slim

# Prevents Python from writing .pyc files to disc and ensures stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first to take advantage of Docker layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create a directory for collected static files (if used)
RUN mkdir -p /vol/web/static
ENV STATIC_ROOT=/vol/web/static

# Create a non-root user for running the app
RUN useradd --create-home --shell /bin/bash nativespeak || true
USER nativespeak

EXPOSE 4000

# Run Gunicorn as default. Adjust worker count as needed for your environment.
CMD ["gunicorn", "nativespeak_api.wsgi:application", "--bind", "0.0.0.0:4000", "--workers", "3"]
