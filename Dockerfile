FROM python:3.11-slim

WORKDIR /app

# Install ONLY essential system deps + ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create required directories
RUN mkdir -p instance logs audio_uploads vector_stores

ENV FLASK_APP=app.main
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

CMD gunicorn "app:create_app()" \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers 2 \
    --timeout 120 \
    --log-level info