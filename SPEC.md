# SPEC.md — Smart Digest (Умный дайджест)

## 1. Concept & Vision

**Умный дайджест** — минималистичное приложение для занятых профессионалов, которое превращает хаос RSS-лент в персонализированные дайджесты. Визуальная метафора — «чистая газета будущего»: типографика как в качественном издании, воздух и фокус на контенте. Никакого информационного шума — только суть.

## 2. Design Language

### Aesthetic Direction
Скандинавский минимализм + газетная типографика. Референс: The Economist digital + Notion. Чистые линии, акцентная типографика, минимум декора.

### Color Palette
```
--bg-primary:    #FAFAF8      (тёплый белый — как качественная бумага)
--bg-card:       #FFFFFF      (чистый белый для карточек)
--bg-accent:    #F5F0E8      (кремовый акцент для hover)
--text-primary:  #1A1A1A     (глубокий чёрный)
--text-secondary:#6B6B6B     (серый для мета-информации)
--text-muted:    #9E9E9E     (светло-серый для дат)
--accent:        #E85D04     (тёплый оранжевый — как свежая типографская краска)
--accent-hover:  #DC4C00     (более тёмный оранжевый)
--tag-bg:        #F0EDE8     (нейтральный тег)
--tag-text:      #5C5C5C     (текст тега)
--success:       #2D6A4F     (зелёный для успеха)
--error:         #D62828      (красный для ошибок)
--border:        #E8E4DE      (мягкая граница)
```

### Typography
- **Headlines**: `Playfair Display` (serif) — 700 weight, fallback: Georgia
- **Body/UI**: `Inter` — 400/500/600, fallback: system-ui
- **Monospace (metadata)**: `JetBrains Mono` — для дат и технических деталей
- **Scale**: 12 / 14 / 16 / 18 / 24 / 32 / 48 px

### Spatial System
- Base unit: 4px
- Card padding: 24px
- Section gaps: 32px
- Max content width: 800px (centered)
- Card border-radius: 8px

### Motion Philosophy
- **Entrance**: Карточки появляются с fade-in + subtle slide-up (opacity 0→1, translateY 12px→0), staggered 80ms, ease-out 300ms
- **Hover**: Карточки приподнимаются (translateY -2px), тень усиливается, 200ms ease
- **Tags**: При появлении — scale 0.9→1, opacity 0→1, 200ms spring
- **Loading**: Skeleton shimmer с градиентом слева направо
- **Page transitions**: Fade 200ms

### Visual Assets
- Icons: Lucide React (stroke-width: 1.5, consistent 20px)
- No decorative images — только контентные картинки из статей (если есть)
- Favicon: стилизованная буква «Д» оранжевого цвета

## 3. Layout & Structure

### Page Architecture

```
┌─────────────────────────────────────────────┐
│  Header: Logo + Nav + Add Feed Button       │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─ Filter Bar ─────────────────────────┐  │
│  │ [Все] [Теги: финансы, IT, дизайн...]  │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌─ Digest Feed ─────────────────────────┐  │
│  │ ┌─ Article Card ───────────────────┐  │  │
│  │ │ Source • Date                     │  │  │
│  │ │ Title (Playfair Display, 24px)   │  │  │
│  │ │ AI Summary (Inter, 16px, 3 lines) │  │  │
│  │ │ [tag] [tag] [tag]  [Read →]       │  │  │
│  │ └───────────────────────────────────┘  │  │
│  │                                         │  │
│  │ (repeating cards, 16px gap)           │  │
│  └───────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

### Responsive Strategy
- **Desktop (>1024px)**: Центрированный контент 800px, полная типографика
- **Tablet (768-1024px)**: 90% ширины, уменьшенные отступы
- **Mobile (<768px)**: Полная ширина, карточки на всю ширину, 16px padding

### Modal: Add Feed
```
┌─────────────────────────────────────┐
│  Add RSS Source               [×]   │
├─────────────────────────────────────┤
│  Feed URL                          │
│  ┌─────────────────────────────┐   │
│  │ https://example.com/rss     │   │
│  └─────────────────────────────┘   │
│                                     │
│  Category (optional)                │
│  ┌─────────────────────────────┐   │
│  │ Technology ▼                │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Cancel]           [Add Feed]     │
└─────────────────────────────────────┘
```

## 4. Features & Interactions

### 4.1 RSS Feed Management
- **Add feed**: Ввод URL → валидация → парсинг → сохранение
- **View feeds**: Список источников в header dropdown
- **Delete feed**: Confirmation tooltip → удаление
- **Refresh**: Кнопка обновления, показывает последнее время синхронизации
- **Auto-refresh**: Каждые 30 минут (в фоне)

### 4.2 Article Digest View
- **Card display**: Source name + timestamp, title, AI summary, tags, "Read original" link
- **Summary length**: 1–3 абзаца (AI определяет оптимальную длину)
- **Empty state**: Friendly message «Ваши дайджесты появятся здесь» с иллюстрацией
- **Loading state**: Skeleton cards (3 штуки) с shimmer-эффектом

### 4.3 AI Summarization
- **Trigger**: При добавлении нового источника или ручном refresh
- **Process**: Fetch article → extract content → send to AI → receive summary
- **Fallback**: Если AI недоступен — показать первые 500 символов статьи
- **Caching**: Summary кэшируется, перегенерация только по запросу

### 4.4 Tagging System
- **Auto-tagging**: AI анализирует контент и предлагает 2–5 тегов
- **Tag display**: Горизонтальный скролл, removable pills
- **Filter by tag**: Клик по тегу фильтрует ленту
- **Preset tags**: Финансы, IT, Дизайн, Маркетинг, Наука, Политика, Культура, Спорт

### 4.5 Search & Filter
- **Search**: Поиск по заголовкам и summary
- **Tag filter**: Мультивыбор тегов
- **Source filter**: По конкретному источнику
- **Sort**: По дате (новые/старые), по источнику

## 5. Component Inventory

### Header
- Logo: «Дайджест» + иконка газеты
- Nav: [Лента] [Источники]
- Actions: [+ Добавить RSS] [⟳ Обновить]
- States: default, loading (spinner on refresh)

### FeedCard
- **Default**: белый фон, мягкая тень, border
- **Hover**: приподнятие, усиленная тень
- **Loading**: skeleton shimmer
- **Error**: красная граница, сообщение об ошибке

### TagPill
- **Default**: нейтральный фон, серый текст
- **Active**: оранжевый фон, белый текст
- **Hover**: затемнение фона
- **Removable**: × иконка справа

### Modal
- **Overlay**: rgba(0,0,0,0.4) с blur
- **Container**: белый, border-radius 12px, max-width 480px
- **Animation**: scale 0.95→1 + fade, 200ms

### Button
- **Primary**: оранжевый фон, белый текст, hover → затемнение
- **Secondary**: белый фон, серая граница, hover → серый фон
- **Ghost**: только текст, hover → подчёркивание
- **Disabled**: opacity 0.5, cursor not-allowed

### Input
- **Default**: белый фон, серая граница
- **Focus**: оранжевая граница, лёгкая тень
- **Error**: красная граница, сообщение под полем
- **With icon**: иконка слева, padding-left для текста

### EmptyState
- Иконка: большая (64px) серая иллюстрация
- Заголовок: «Пока пусто»
- Подзаголовок: контекстная подсказка
- CTA: кнопка добавления источника

## 6. Technical Approach

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── FeedCard.jsx
│   │   ├── TagPill.jsx
│   │   ├── AddFeedModal.jsx
│   │   ├── FilterBar.jsx
│   │   ├── EmptyState.jsx
│   │   └── SkeletonCard.jsx
│   ├── hooks/
│   │   ├── useFeeds.js
│   │   └── useArticles.js
│   ├── api/
│   │   └── index.js
│   ├── App.jsx
│   ├── App.css
│   └── main.jsx
├── index.html
├── vite.config.js
└── package.json
```

### Backend (Python + FastAPI)
```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── rss_parser.py     # RSS/Atom parsing
│   ├── summarizer.py     # AI integration
│   ├── storage.py        # JSON file storage
│   └── models.py         # Pydantic models
├── requirements.txt
└── .env.example
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/feeds` | List all RSS sources |
| POST | `/api/feeds` | Add new RSS source |
| DELETE | `/api/feeds/{id}` | Remove RSS source |
| GET | `/api/articles` | List articles with summaries |
| POST | `/api/articles/{id}/refresh` | Force re-summarize article |
| GET | `/api/tags` | List available tags |
| POST | `/api/summarize` | Manual summarize endpoint |

### Data Models

```python
# Feed
{
    "id": "uuid",
    "url": "https://example.com/rss",
    "title": "Source Name",
    "category": "Technology",
    "added_at": "2024-01-15T10:30:00Z",
    "last_fetched": "2024-01-15T12:00:00Z"
}

# Article
{
    "id": "uuid",
    "feed_id": "uuid",
    "title": "Article Title",
    "url": "https://example.com/article",
    "published": "2024-01-15T09:00:00Z",
    "summary": "AI-generated summary...",
    "tags": ["финансы", "технологии"],
    "content": "Full article text...",
    "image_url": "optional-thumbnail.jpg"
}
```

### AI Integration
- Configurable provider: OpenAI, Anthropic, or mock mode
- Environment variables: `AI_PROVIDER`, `AI_API_KEY`
- Fallback: Mock summarizer returns truncated content + random tags
- Rate limiting: Max 10 requests/minute

### Storage
- JSON files in `backend/data/` directory
- `feeds.json`: список источников
- `articles.json`: articles with summaries
- Atomic writes with temp file pattern

### Dependencies

**Frontend:**
- react, react-dom
- lucide-react (icons)
- vite

**Backend:**
- fastapi, uvicorn
- feedparser (RSS parsing)
- httpx (async HTTP)
- beautifulsoup4 (HTML cleaning)
- pydantic
- python-dotenv
- aiofiles (async file ops)

---

*Document version: 1.0*
*Created for: Smart Digest MVP*
