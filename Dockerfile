FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance logs audio_uploads vector_stores/faiss

ENV FLASK_APP=app.main
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# ✅ FIXED: use shell form (not array form) so $PORT resolves
CMD gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info