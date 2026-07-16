"""Pydantic models for Smart Digest API."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class FeedCreate(BaseModel):
    """Schema for creating a new feed."""
    url: str = Field(..., description="RSS/Atom feed URL")
    category: Optional[str] = Field(None, description="Optional category")


class Feed(BaseModel):
    """Full feed representation."""
    id: str
    url: str
    title: str
    category: Optional[str] = None
    added_at: datetime
    last_fetched: Optional[datetime] = None


class Article(BaseModel):
    """Article with AI-generated summary."""
    id: str
    feed_id: str
    feed_title: str
    title: str
    url: str
    published: Optional[datetime] = None
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    content: Optional[str] = None
    image_url: Optional[str] = None


class ArticleRefresh(BaseModel):
    """Response after refreshing an article."""
    id: str
    status: str
    summary: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TagsResponse(BaseModel):
    """Available tags response."""
    tags: List[str]


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
