# Smart Digest — Dockerfile
# Multi-stage build для оптимизации размера

# ============ Build Stage ============
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Копируем package files
COPY frontend/package*.json ./
RUN npm ci

# Копируем исходники frontend
COPY frontend/ ./
RUN npm run build

# ============ Backend Stage ============
FROM python:3.11-slim AS backend

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python зависимости
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Копируем backend код
COPY backend/ ./backend/

# Создаём директорию для данных
RUN mkdir -p /app/backend/data

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Gunicorn для production
EXPOSE 8000

CMD ["sh", "-c", "cd backend && gunicorn main:app --host 0.0.0.0 --port 8000 --workers 2"]
