"""JSON file storage for feeds and articles."""
import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiofiles

DATA_DIR = Path(__file__).parent.parent / "data"
FEEDS_FILE = DATA_DIR / "feeds.json"
ARTICLES_FILE = DATA_DIR / "articles.json"


def _ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json_sync(filepath: Path) -> dict:
    """Load JSON file synchronously (for startup)."""
    _ensure_data_dir()
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


async def load_json(filepath: Path) -> dict:
    """Load JSON file asynchronously."""
    _ensure_data_dir()
    if filepath.exists():
        async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content) if content else {}
    return {}


async def save_json(filepath: Path, data: dict):
    """Save JSON file atomically."""
    _ensure_data_dir()
    temp_path = filepath.with_suffix(".tmp")
    content = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    
    async with aiofiles.open(temp_path, "w", encoding="utf-8") as f:
        await f.write(content)
    
    temp_path.replace(filepath)


class Storage:
    """Storage manager for feeds and articles."""
    
    def __init__(self):
        _ensure_data_dir()
        self._lock = asyncio.Lock()
    
    async def get_feeds(self) -> list[dict]:
        """Get all feeds."""
        data = await load_json(FEEDS_FILE)
        return data.get("feeds", [])
    
    async def get_feed(self, feed_id: str) -> Optional[dict]:
        """Get a specific feed by ID."""
        feeds = await self.get_feeds()
        for feed in feeds:
            if feed["id"] == feed_id:
                return feed
        return None
    
    async def add_feed(self, url: str, title: str, category: Optional[str] = None) -> dict:
        """Add a new feed."""
        async with self._lock:
            feeds = await self.get_feeds()
            
            # Check for duplicate URL
            for feed in feeds:
                if feed["url"] == url:
                    return feed
            
            new_feed = {
                "id": str(uuid.uuid4()),
                "url": url,
                "title": title,
                "category": category,
                "added_at": datetime.utcnow().isoformat(),
                "last_fetched": None
            }
            feeds.append(new_feed)
            
            data = await load_json(FEEDS_FILE)
            data["feeds"] = feeds
            await save_json(FEEDS_FILE, data)
            
            return new_feed
    
    async def delete_feed(self, feed_id: str) -> bool:
        """Delete a feed and its articles."""
        async with self._lock:
            feeds = await self.get_feeds()
            feeds = [f for f in feeds if f["id"] != feed_id]
            
            data = await load_json(FEEDS_FILE)
            data["feeds"] = feeds
            await save_json(FEEDS_FILE, data)
            
            # Also delete articles for this feed
            articles_data = await load_json(ARTICLES_FILE)
            articles_data["articles"] = [
                a for a in articles_data.get("articles", [])
                if a.get("feed_id") != feed_id
            ]
            await save_json(ARTICLES_FILE, articles_data)
            
            return True
    
    async def update_feed_fetch_time(self, feed_id: str):
        """Update last_fetched timestamp for a feed."""
        feeds = await self.get_feeds()
        for feed in feeds:
            if feed["id"] == feed_id:
                feed["last_fetched"] = datetime.utcnow().isoformat()
                break
        
        data = await load_json(FEEDS_FILE)
        data["feeds"] = feeds
        await save_json(FEEDS_FILE, data)
    
    async def get_articles(self, feed_id: Optional[str] = None, 
                          tags: Optional[list[str]] = None,
                          search: Optional[str] = None) -> list[dict]:
        """Get articles with optional filtering."""
        data = await load_json(ARTICLES_FILE)
        articles = data.get("articles", [])
        
        # Filter by feed
        if feed_id:
            articles = [a for a in articles if a.get("feed_id") == feed_id]
        
        # Filter by tags
        if tags:
            articles = [a for a in articles 
                       if any(tag in a.get("tags", []) for tag in tags)]
        
        # Filter by search query
        if search:
            search_lower = search.lower()
            articles = [a for a in articles
                       if search_lower in a.get("title", "").lower()
                       or search_lower in a.get("summary", "").lower()]
        
        # Sort by published date (newest first)
        articles.sort(key=lambda x: x.get("published") or "", reverse=True)
        
        return articles
    
    async def get_article(self, article_id: str) -> Optional[dict]:
        """Get a specific article by ID."""
        articles = await self.get_articles()
        for article in articles:
            if article["id"] == article_id:
                return article
        return None
    
    async def add_article(self, article: dict) -> dict:
        """Add or update an article."""
        async with self._lock:
            articles_data = await load_json(ARTICLES_FILE)
            articles = articles_data.get("articles", [])
            
            # Check if article already exists (by URL)
            for i, existing in enumerate(articles):
                if existing.get("url") == article.get("url"):
                    # Update existing article
                    articles[i] = {**existing, **article}
                    articles_data["articles"] = articles
                    await save_json(ARTICLES_FILE, articles_data)
                    return articles[i]
            
            # Add new article
            new_article = {
                "id": str(uuid.uuid4()),
                **article
            }
            articles.append(new_article)
            articles_data["articles"] = articles
            await save_json(ARTICLES_FILE, articles_data)
            
            return new_article
    
    async def update_article(self, article_id: str, updates: dict) -> Optional[dict]:
        """Update an article's fields."""
        async with self._lock:
            articles_data = await load_json(ARTICLES_FILE)
            articles = articles_data.get("articles", [])
            
            for i, article in enumerate(articles):
                if article["id"] == article_id:
                    articles[i] = {**article, **updates}
                    articles_data["articles"] = articles
                    await save_json(ARTICLES_FILE, articles_data)
                    return articles[i]
            
            return None
    
    async def get_all_tags(self) -> list[str]:
        """Get all unique tags from articles."""
        articles = await self.get_articles()
        tags = set()
        for article in articles:
            tags.update(article.get("tags", []))
        return sorted(list(tags))


# Singleton instance
storage = Storage()
