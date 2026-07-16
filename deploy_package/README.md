# Smart Digest — Инструкция по установке

## Структура

```
smart-digest/
├── backend/           # Python FastAPI приложение
│   ├── app/
│   │   ├── main.py
│   │   ├── rss_parser.py
│   │   ├── summarizer.py
│   │   ├── storage.py
│   │   └── models.py
│   └── requirements.txt
├── frontend/          # Собранный React (статика)
│   └── index.html
├── nginx.conf         # Конфиг nginx
├── start.sh           # Скрипт запуска
└── SPEC.md            # Документация проекта
```

## Быстрая установка (Ubuntu/Debian)

```bash
# 1. Установка nginx и Python
apt update && apt install -y nginx python3 python3-pip

# 2. Копируем файлы
cp -r frontend /var/www/smart-digest
cp nginx.conf /etc/nginx/sites-available/smart-digest

# 3. Активируем сайт
ln -s /etc/nginx/sites-available/smart-digest /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # если нужен только наш сайт

# 4. Проверяем и перезапускаем nginx
nginx -t && systemctl reload nginx

# 5. Устанавливаем зависимости Python
cd путь/к/smart-digest
pip install -r requirements.txt

# 6. Запускаем бэкенд
chmod +x start.sh
./start.sh
```

## Настройка AI (опционально)

Для включения AI-суммаризации создайте файл `backend/.env`:

```env
AI_PROVIDER=openai
AI_API_KEY=ваш-api-ключ
```

Без API-ключа работает режим демо (без AI).

## Проверка

- Главная страница: `http://ваш-сервер/`
- API документация: `http://ваш-сервер/api/docs`
