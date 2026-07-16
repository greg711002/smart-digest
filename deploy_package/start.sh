#!/bin/bash

# Smart Digest — скрипт запуска

# Устанавливаем зависимости Python
pip install -r requirements.txt

# Запускаем бэкенд в фоне
cd backend/app
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload >/var/log/smart-digest-backend.log 2>&1 &

echo "Smart Digest запущен!"
echo "Backend API: http://localhost:8000"
echo "Swagger docs: http://localhost:8000/docs"
