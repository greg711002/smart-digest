# Smart Digest — Умный дайджест

Минималистичное приложение для занятых профессионалов, которое превращает RSS-ленты в персонализированные дайджесты с AI-суммаризацией.

![Design Preview](https://via.placeholder.com/800x400?text=Smart+Digest+Preview)

## Возможности

- 📰 **Управление RSS-лентами** — добавление, удаление, автообновление
- 🤖 **AI-суммаризация** — краткие дайджесты вместо длинных статей
- 🏷️ **Система тегов** — фильтрация по категориям
- 🔍 **Поиск** — быстрый поиск по заголовкам и содержанию
- 📱 **Адаптивный дизайн** — работает на любых устройствах

## Tech Stack

- **Frontend:** React + Vite + Lucide Icons
- **Backend:** FastAPI + Uvicorn + Gunicorn
- **Парсинг:** Feedparser + BeautifulSoup4
- **AI:** OpenAI / Anthropic (опционально)
- **Хостинг:** Docker, Railway, Render, Fly.io

## Быстрый старт

### Docker (рекомендуется)

```bash
git clone <repo-url> smart-digest
cd smart-digest
docker compose up -d --build
```

Откройте http://localhost:3000

### Без Docker

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (в отдельном терминале)
cd frontend
npm install
npm run dev
```

## Деплой

Подробная инструкция: [DEPLOY.md](deploy_package/DEPLOY.md)

### Railway (самый простой)

```bash
railway init
railway up
```

### Fly.io

```bash
fly launch
fly deploy
```

### VPS

```bash
docker compose up -d
```

## Переменные окружения

```env
AI_PROVIDER=openai      # openai, anthropic, mock
AI_API_KEY=your-key     # API ключ для AI
PORT=8000
```

## API Endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /api/feeds` | Список RSS источников |
| `POST /api/feeds` | Добавить источник |
| `DELETE /api/feeds/{id}` | Удалить источник |
| `GET /api/articles` | Статьи с суммаризациями |
| `GET /api/docs` | Swagger документация |

## Структура проекта

```
smart-digest/
├── backend/              # FastAPI приложение
│   ├── app/
│   │   ├── main.py       # Роутеры и конфигурация
│   │   ├── rss_parser.py # Парсинг RSS/Atom
│   │   ├── summarizer.py  # AI интеграция
│   │   ├── storage.py     # JSON storage
│   │   └── models.py      # Pydantic модели
│   └── requirements.txt
├── frontend/             # React приложение
│   ├── src/
│   ├── dist/             # Собранные файлы
│   └── package.json
├── deploy_package/       # Конфиги для деплоя
│   ├── nginx.conf
│   ├── start.sh
│   └── DEPLOY.md
├── Dockerfile
├── docker-compose.yml
└── SPEC.md              # Дизайн-спецификация
```

## Лицензия

MIT
