# Smart Digest — Инструкция по деплою

## Варианты хостинга

### 1. Docker (любой VPS/сервер)

```bash
# Клонируем проект
git clone <repo-url> smart-digest
cd smart-digest

# Собираем и запускаем
docker compose up -d --build

# Проверяем
curl http://localhost:3000
```

**Переменные окружения:**
```bash
AI_PROVIDER=openai
AI_API_KEY=your-key
```

---

### 2. Railway (рекомендуется для простоты)

1. Создайте аккаунт на [Railway](https://railway.app)
2. New Project → Deploy from GitHub
3. Выберите репозиторий
4. Railway автоматически определит Dockerfile

**Или через CLI:**
```bash
npm install -g @railway/cli
railway login
cd smart-digest
railway init
railway up
```

---

### 3. Render

1. Создайте аккаунт на [Render](https://render.com)
2. New → Web Service
3. Подключите GitHub репозиторий
4. Build Command: оставьте пустым (используйте Dockerfile)
5. Start Command: `cd backend && gunicorn main:app --host 0.0.0.0 --port $PORT`

---

### 4. Fly.io

```bash
# Установите flyctl
curl -L https://fly.io/install.sh | sh

# Логин
fly auth login

# Деплой
cd smart-digest
fly launch
fly deploy
```

---

### 5. VPS (ручная установка)

```bash
# Установка Docker на Ubuntu
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Или без Docker — напрямую
apt install -y python3-pip nginx
cd smart-digest/backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Структура Docker-образа

```
smart-digest/
├── Dockerfile          # Multi-stage build
├── docker-compose.yml  # Production stack
├── frontend/dist/      # Собранный frontend
└── backend/            # Python API
```

## API Endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /` | Frontend SPA |
| `GET /api/feeds` | Список RSS источников |
| `POST /api/feeds` | Добавить источник |
| `DELETE /api/feeds/{id}` | Удалить источник |
| `GET /api/articles` | Статьи с суммаризациями |
| `GET /api/docs` | Swagger документация |

## Troubleshooting

**Контейнер не стартует:**
```bash
docker logs smart-digest-backend
docker logs smart-digest-frontend
```

**Пересборка:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

**Логи в реальном времени:**
```bash
docker compose logs -f
```

**Перезапуск:**
```bash
docker compose restart backend
```

## Production Checklist

- [ ] Настроить AI_PROVIDER и AI_API_KEY
- [ ] Включить HTTPS (через Cloudflare или Traefik)
- [ ] Настроить резервное копирование данных
- [ ] Мониторинг (опционально)
