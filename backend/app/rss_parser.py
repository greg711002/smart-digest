"""RSS/Atom feed parser."""
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import feedparser
import httpx
from bs4 import BeautifulSoup


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse various date formats from RSS feeds."""
    if not date_str:
        return None
    
    # feedparser normalizes dates
    if hasattr(date_str, 'parsed'):
        return datetime(*date_str.timetuple()[:6])
    
    # Try common formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.replace(' +0000', ' +0000').replace(' UTC', ' +0000'), fmt)
        except ValueError:
            continue
    
    return None


def clean_html(html: str, max_length: int = 5000) -> str:
    """Clean HTML and extract plain text."""
    if not html:
        return ""
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
        script.decompose()
    
    # Get text
    text = soup.get_text(separator=' ', strip=True)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate if needed
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text


def extract_image(entry) -> Optional[str]:
    """Extract image URL from RSS entry."""
    # Check media_content
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
    
    # Check enclosures
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enclosure in entry.enclosures:
            if enclosure.get('type', '').startswith('image/'):
                return enclosure.get('url')
    
    # Check content
    content = entry.get('content') or entry.get('summary') or ''
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'):
            return img.get('src')
    
    return None


async def parse_feed(url: str) -> dict:
    """Parse an RSS/Atom feed and return feed metadata."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch feed: {e}")
    
    feed = feedparser.parse(response.text)
    
    if feed.bozo and not feed.entries:
        raise ValueError("Invalid or empty RSS feed")
    
    # Get feed metadata
    feed_info = {
        "title": feed.feed.get("title", urlparse(url).netloc),
        "description": feed.feed.get("description", ""),
        "link": feed.feed.get("link", ""),
        "entries_count": len(feed.entries),
    }
    
    return feed_info


async def fetch_feed_entries(url: str, limit: int = 20) -> list[dict]:
    """Fetch and parse entries from an RSS/Atom feed."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch feed: {e}")
    
    feed = feedparser.parse(response.text)
    
    if feed.bozo and not feed.entries:
        raise ValueError("Invalid or empty RSS feed")
    
    entries = []
    for entry in feed.entries[:limit]:
        # Get the best content available
        content = None
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if hasattr(entry.content[0], 'value') else str(entry.content[0])
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # Get the best link
        link = entry.get("link") or entry.get("id", "")
        
        # Get published date
        published = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6])
        
        entries.append({
            "title": entry.get("title", "Untitled"),
            "url": link,
            "published": published.isoformat() if published else None,
            "content": content,
            "image_url": extract_image(entry),
        })
    
    return entries
