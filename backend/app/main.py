"""Smart Digest API - FastAPI application."""
import asyncio
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    Feed, FeedCreate, Article, ArticleRefresh, 
    TagsResponse, ErrorResponse
)
from .storage import storage
from .rss_parser import parse_feed, fetch_feed_entries, clean_html
from .summarizer import get_summarizer_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: nothing special needed
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="Smart Digest API",
    description="AI-powered RSS digest generator for busy professionals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/feeds", response_model=list[Feed])
async def list_feeds():
    """Get all RSS feeds."""
    feeds = await storage.get_feeds()
    return feeds


@app.post("/api/feeds", response_model=Feed, status_code=201)
async def add_feed(feed_data: FeedCreate):
    """Add a new RSS feed source."""
    try:
        # Validate feed URL
        feed_info = await parse_feed(feed_data.url)
        
        # Add to storage
        feed = await storage.add_feed(
            url=feed_data.url,
            title=feed_info["title"],
            category=feed_data.category
        )
        
        # Fetch and process entries in background
        asyncio.create_task(_process_feed_entries(feed["id"], feed_data.url))
        
        return feed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add feed: {str(e)}")


@app.delete("/api/feeds/{feed_id}")
async def delete_feed(feed_id: str):
    """Delete an RSS feed and its articles."""
    feed = await storage.get_feed(feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    await storage.delete_feed(feed_id)
    return {"status": "deleted", "feed_id": feed_id}


@app.get("/api/articles", response_model=list[Article])
async def list_articles(
    feed_id: Optional[str] = Query(None, description="Filter by feed ID"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter"),
    search: Optional[str] = Query(None, description="Search in title and summary")
):
    """Get articles with summaries."""
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    articles = await storage.get_articles(
        feed_id=feed_id,
        tags=tag_list,
        search=search
    )
    return articles


@app.post("/api/articles/{article_id}/refresh", response_model=ArticleRefresh)
async def refresh_article(article_id: str):
    """Force re-summarize an article."""
    article = await storage.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    summarizer = get_summarizer_instance()
    
    # Re-summarize
    if article.get("content"):
        content = article["content"]
    else:
        # Fetch content again (simplified - just use title)
        content = article.get("title", "")
    
    summary, tags = await summarizer.summarize(article["title"], content)
    
    # Update in storage
    await storage.update_article(article_id, {
        "summary": summary,
        "tags": tags
    })
    
    return ArticleRefresh(
        id=article_id,
        status="refreshed",
        summary=summary,
        tags=tags
    )


@app.get("/api/tags", response_model=TagsResponse)
async def list_tags():
    """Get all available tags."""
    tags = await storage.get_all_tags()
    return TagsResponse(tags=tags)


@app.post("/api/refresh-all")
async def refresh_all_feeds():
    """Refresh all feeds and fetch new articles."""
    feeds = await storage.get_feeds()
    results = []
    
    for feed in feeds:
        try:
            await _process_feed_entries(feed["id"], feed["url"])
            results.append({"feed_id": feed["id"], "status": "success"})
        except Exception as e:
            results.append({"feed_id": feed["id"], "status": "error", "error": str(e)})
    
    return {"results": results}


async def _process_feed_entries(feed_id: str, url: str):
    """Process RSS feed entries and generate summaries."""
    summarizer = get_summarizer_instance()
    feed = await storage.get_feed(feed_id)
    
    if not feed:
        return
    
    entries = await fetch_feed_entries(url, limit=20)
    
    for entry in entries:
        # Clean content
        content = clean_html(entry.get("content", "")) if entry.get("content") else ""
        
        # Generate summary
        summary, tags = await summarizer.summarize(entry.get("title", ""), content)
        
        # Create article record
        article_data = {
            "feed_id": feed_id,
            "feed_title": feed["title"],
            "title": entry.get("title", "Untitled"),
            "url": entry.get("url", ""),
            "published": entry.get("published"),
            "summary": summary,
            "tags": tags,
            "content": content,
            "image_url": entry.get("image_url")
        }
        
        await storage.add_article(article_data)
    
    # Update feed fetch time
    await storage.update_feed_fetch_time(feed_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
